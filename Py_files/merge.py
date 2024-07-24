import pandas as pd 
import numpy as np 
## Merge dfs from two lists
def mergefromlists(main_frame,second_frame,common_col,mf_name,sf_name,how="left"):
    """
    main frame: Major frame 
    second frame: Secondary frame 

    mf_name: Querying on filenames for matching 
    sf_name: secondary column for querying
    """
    new_list=[]
    for outer in range(len(main_frame)):
        # print(2)
        for inner in range(len(second_frame)):
            if main_frame[outer][mf_name].iloc[0]==second_frame[inner][sf_name].iloc[0]:
                print(main_frame[outer].shape,second_frame[inner].shape)
                new_list.append(pd.merge(main_frame[outer],second_frame[inner],on=common_col,how=how))
    return new_list