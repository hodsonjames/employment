from functools import lru_cache
import warnings

import pandas as pd

import science.profile2vec.title_crf_components as crf


tag_title = crf.TagTitle()


@lru_cache(maxsize=None)
def split_title(title):
    d = tag_title.tag_text(title)
    department = d['DEPARTMENT'][0][3] if 'DEPARTMENT' in d else None
    if department is not None:
        left, right = title.split(department, maxsplit=1)
        left = left.rstrip(' ,-|')
        right = right.lstrip(' ,-|')
        if left.endswith(' of'):
            left = left[:-3].rstrip(' ,-|')
        if right.startswith('Division'):
            right = right[8:].lstrip(' ,-|')
        sep = ' ' if left and right else ''
        title = left + sep + right
        if department.endswith('Division'):
            department = department[:-8].rstrip(' ,-|')
    return pd.Series([department, title])


def main(source_file, target_file):
    """
    Split the role titles in the source tsv transitions file into department
    and the rest and add those parts as columns to the right of existing ones:
        source_dept, source_role, target_dept, target_role
    """
    df = pd.read_csv(source_file, sep='\t', header=None, encoding='utf-8',
                     memory_map=True, engine='c', dtype='str')
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        roles1 = df.loc[:, 17].apply(split_title)
        roles2 = df.loc[:, 31].apply(split_title)
    df2 = pd.concat([df, roles1, roles2], axis=1, ignore_index=True)
    df2.to_csv(target_file, sep='\t', header=False, index=False)


if __name__ == '__main__':
	# main(r'Z:\graph_transitions\goldman.tsv', r'Z:\graph_transitions\goldman_dept.tsv')
	pass
