import sys
import pickle
import time
import ast
import json

## Global variables

# Primary Index Metadata
Metadata = {}
No_Split_Files = 0

# Secondary Index
Secondary_Index = {}

# Merging
File_Pointer_Arr = []
Output_File_No = 0
Output_Buffer = {}
Output_Threshold = 2000000


## Heap Node class
class HeapNode():
    def __init__(self, Term="", PostingList={}, FilePointer=None):
        self.Term = Term
        self.PostingList = PostingList
        self.FilePointer = FilePointer

## Heapify Method
def Min_Heapify(arr, n, i):

    smallest = i
    left = 2*i + 1
    right = 2*i + 2

    # See if left child of root exists and is greater than root
    if left < n and arr[left].Term < arr[i].Term:
        smallest = left

    # See if right child of root exists and is greater than root
    if right < n and  arr[right].Term < arr[smallest].Term:
        smallest = right

    # Change root, if needed
    if smallest != i:
        (arr[i],arr[smallest]) = (arr[smallest],arr[i])
        # Heapify the root.
        arr = Min_Heapify(arr, n, smallest)
    return arr

## Create Heap Method
def Create_Heap(arr):

    n = len(arr)
    for i in range(int(n/2+1), -1, -1):
        arr = Min_Heapify(arr, n, i)

    return arr

## Load Primary Index Metadata file
def Load_PriIndex_Metadata(path_to_index_folder):

    global Metadata
    global No_Split_Files

    with open(path_to_index_folder+"/metadata.pkl", "rb") as file:
        Metadata = pickle.load(file)

    No_Split_Files = Metadata["No_Files"]

## Load and Open Multiple files Method
def Laod_Split_Files(path_to_index_folder):

    global File_Pointer_Arr
    for file_no in range(No_Split_Files):
        file_pointer = open(path_to_index_folder+"/index"+str(file_no+1)+".txt", "r")
        File_Pointer_Arr.append(file_pointer)

## Merge multiple key entries to single entry
def Merge_Terms(Duplicate_Entry):

    global Output_Buffer
    OP_Buffer_Entry = Output_Buffer[Duplicate_Entry.Term]
    Merged_Entry = {}

    for DocID in OP_Buffer_Entry.keys():
        if DocID in Duplicate_Entry.PostingList.keys():
            Merged_Entry[DocID] = {}
            for key in OP_Buffer_Entry[DocID]:
                if key in Duplicate_Entry.PostingList[DocID]:
                    Merged_Entry[DocID][key] = OP_Buffer_Entry[DocID][key] + Duplicate_Entry.PostingList[DocID][key]

    Output_Buffer[Duplicate_Entry.Term] = Merged_Entry

## Flush output_buffer
def Flush_OutputBuffer(path_to_index_folder, Last_Min_Element):
    global Output_File_No
    global Secondary_Index
    global Output_Buffer

    # print("FLUSING OUTPUT BUFFER")
    # print(Output_Buffer)

    Output_File_No += 1
    Secondary_Index[Last_Min_Element.Term] = Output_File_No

    # with open(path_to_index_folder+"/MergedIndex"+str(Output_File_No)+".pkl", "wb") as file:
    #     pickle.dump(Output_Buffer,file)

    with open(path_to_index_folder+"/MergedIndex"+str(Output_File_No)+".json", "w") as jsonfile:
        json.dump(Output_Buffer,jsonfile)
    Output_Buffer = {}

## Store secondary index in file (which file no contains primary index till which word)
def Store_Secondary_Index(path_to_index_folder):
    global Secondary_Index

    with open(path_to_index_folder+"/secondary_index.pkl", "wb") as Sec_Index:
        pickle.dump(Secondary_Index, Sec_Index)

    print("SECONDARY INDEX: ", Secondary_Index)

## Merge Method (Create list of heapnodes, k-way merge algo)
def Merge_Index(path_to_index_folder):

    # Create array of file pointers of opened index files
    Laod_Split_Files(path_to_index_folder)
    HeapNodes = []

    # Create array of heap_objects
    for file_pointer in File_Pointer_Arr:

        line = file_pointer.readline()
        if len(line) != 0:

            line_tokens = line.split("=")
            index_key = line_tokens[0].strip()
            index_val = ast.literal_eval(line_tokens[1])

            HeapNode_Obj = HeapNode(index_key, index_val, file_pointer)
        else :
            HeapNode_Obj = HeapNode(sys.maxint, {}, None)
        HeapNodes.append(HeapNode_Obj)

    # Create Min-heap og HeapNode objects
    HeapNodes = Create_Heap(HeapNodes)

    # Write top element of heap in output buffer, Add new element to heap from
    # corresponding file pointer, and loop till all files are read
    Last_Min_Element = HeapNodes[0]
    while True:
        Min_Element = HeapNodes[0]

        if Min_Element.Term == "zzzzzz":
            break

        if Min_Element.Term in Output_Buffer.keys():
            Merge_Terms(Min_Element)

        if sys.getsizeof(Output_Buffer) >= Output_Threshold:
            Flush_OutputBuffer(path_to_index_folder, Last_Min_Element)

        Output_Buffer[Min_Element.Term] = Min_Element.PostingList

        Current_FileHandler = Min_Element.FilePointer
        line = Current_FileHandler.readline()
        if len(line) == 0:
            index_key = "zzzzzz"
            index_val = {}
        else:
            line_tokens = line.split("=")
            index_key = line_tokens[0].strip()
            index_val = ast.literal_eval(line_tokens[1])

        HeapNodes[0] = HeapNode(index_key, index_val, Current_FileHandler)
        HeapNodes = Min_Heapify(HeapNodes, len(HeapNodes), 0)
        Last_Min_Element = Min_Element

    Flush_OutputBuffer(path_to_index_folder, Last_Min_Element)

if __name__ == "__main__":

    start = time.time()
    No_Split_Files = 5
    Merge_Index("/Users/pranjali/Documents/Wiki_Search_Engine/Index")
    Store_Secondary_Index("/Users/pranjali/Documents/Wiki_Search_Engine/Index")
    end = time.time()

    print("MERGE INDEX TIME: ", end - start)
