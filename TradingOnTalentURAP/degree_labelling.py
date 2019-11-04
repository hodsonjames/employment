import pandas as pd

# Labelling Function

def assign_labels(df, direct_keywords, direct_star_keywords, exclude_keywords, tangential_keywords):

    df_direct = df[df.Degree.str.contains('|'.join(direct_keywords), case = False)]

    df_direct = df_direct[~df_direct.Degree.str.contains('|'.join(exclude_keywords), case = False)]
    
    df_without_exclude = df[~df.Degree.str.contains('|'.join(set(df_direct.Degree)), case = False, regex = False)]
    
    df_tangential = df_without_exclude[df_without_exclude.Degree.str.contains('|'.join(tangential_keywords), case = False)]
    
    df_direct_star = df_without_exclude[df_without_exclude.Degree.str.contains('|'.join(direct_star_keywords), case = False)]
    
    df_labels = []
    for index, row in df.iterrows():
        if row['Degree'] in set(df_direct.Degree):
            df_labels.append('direct')
        elif row['Degree'] in set(df_tangential.Degree):
            df_labels.append('indirect')
        elif row['Degree'] in set(df_direct_star.Degree):
            df_labels.append('direct*')
        else:
            df_labels.append("None")
        
    df['Label'] = df_labels
    
    return df

 # Load in all dataframes

dfs = {}
universities = ['anna university.csv', 
                'arizona state university.csv',
               'cornell university.csv',
               'michigan state university.csv',
               'new york university.csv',
               'penn state university.csv',
               'purdue university.csv',
               'texas a&m university.csv',
               'the ohio state university.csv',
               'the university of texas at austin.csv',
               'universidad complutense de madrid.csv',
               'university of california, berkeley.csv',
               'university of florida.csv',
               'university of illinois at urbana-champaign.csv',
               'university of michigan.csv',
               'university of mumbai.csv',
               'university of phoenix.csv',
               'university of southern california.csv',
               'university of toronto.csv',
               'university of washington.csv']

for uni in universities:
    df = pd.read_csv("/Users/jacquelinewood/Documents/URAP/Universities_Unlabelled/" +, header = None)
    df = df.rename(columns={0: 'Degree', 1: '# Students'})
    dfs[uni[:-4]] = df

# Label dataframes

for uni in dfs:
    df = assign_labels(dfs[uni], direct_keywords = [
            "machine learning",
            "artificial intelligence",
            "natural language processing",
                                                   "computer vision",
                                                   "robotics",
                                                   "ML engineering",
                                                   "AI systems"],
                       direct_star_keywords = ["data science","data analytics", "big data"],
                   exclude_keywords = ['business','system','management','technology','communications','design',
                                                                      'database',
                                                                      'structures',
                                                                      "data networks",
                                                                      "machine perception",
                                                                      "information studies",
                                                                      "warehousing",
                                                                      "library",
                                                                      "journalism","media",
                                                                 "mgmt","sports","estate","geo",
                    "architecture","marketing","security","health","informatics","tool","information t"],
                   tangential_keywords = ["computer",
                      "stati",
                      "info","applied math","informatics"])
    
    dfs[uni] = df

# Write to csvs

for uni in dfs:
    
    dfs[uni].to_csv("/Users/jacquelinewood/Documents/URAP/Universities_Labelled/" + uni + ' labelled.csv')









