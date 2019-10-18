import pandas as pd
from glob import glob


def main(source_glob, target_file, ticker):
    """ 
    Copy only those transitions from the source transition tsv files that
    involve a company with the given ticker and copy them to the target file
    """
    out_lines = 0
    with open(target_file, mode='a', encoding='utf-8', newline='') as f:
        for filename in glob(source_glob):
            print('Processing', filename)
            df = pd.read_csv(filename, sep='\t', header=None, encoding='utf-8',
                             memory_map=True, engine='c', dtype='str')
            goldman_df = df[(df.loc[:, 20].fillna('') == ticker) | (df.loc[:, 34].fillna('') == ticker)]
            out_lines += len(goldman_df)
            goldman_df.to_csv(f, sep='\t', mode='a', header=False, index=False)
            del df
            del goldman_df
    print(f'Printed {out_lines} lines.')


if __name__ == '__main__':
	# main(r'Z:\graph_transitions\export_*.tsv', r'Z:\graph_transitions\goldman.tsv', 'GS')
	pass
