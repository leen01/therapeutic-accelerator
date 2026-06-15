""" 
Parse all of the .json.gz files into pargquet files for easier manipulation later

Takes the annotations that indicate information using {"end":123, "start":001} to extract text from each paper

"""

# %load_ext cudf.pandas
import cudf
import cudf.pandas
# cudf.pandas.install()

import pandas as pd
from tqdm.auto import tqdm
import logging
from glob import glob
from pathlib import Path
import numpy as np
import pyarrow as pa
from ast import literal_eval
import re
import duckdb
# import cudf


def parse_text(annotations, text):
    # some text is still not being extracted
    parsed_text = {}
    for k, v in annotations.items():
        if v:
            parsed_text[k] = []
            # text = new_df.loc[0, 'text']
            try:
                locations = pd.DataFrame(literal_eval(v)).values
                for l in locations:
                    extracted_text = text[l[1]:l[0]].strip()
                    parsed_text[k].append(extracted_text)
            except:
                pass
        try:
            if k in ['title', 'author', 'abstract']:
                parsed_text[k] = ','.join(parsed_text[k])
        except:
            pass
    if len(parsed_text) == 0:
        return None
    else:
        parsed_text['text_len'] = len(text)
        return parsed_text


def pull_major_sections(parsed_text, section_headers):
    """ 
    parsed_text contains the text split by sections and is a dict
    section_headers is the location of the headers based on the annotations
    """
    # pull out major sections
    major_sections = ['Background', 'Methods',
                      'Results', 'Conclusion', 'Discussion']

    try:
        sections_dict = dict(zip(parsed_text['sectionheader'], pd.DataFrame(
            literal_eval(section_headers)).values))
        sections = pd.DataFrame(sections_dict).T
        sections = sections[sections.index.str.contains(
            '|'.join(major_sections), flags=re.IGNORECASE)]
        sections['next_section_start'] = np.roll(sections[1], -1)
        sections.iloc[-1, 2] = parsed_text['text_len']
        sections = sections.iloc[:, 1:].reset_index().values
    except:
        parsed_text

    return sections


def connect_paragraphs(parsed_text, annotations):
    # connect sections to paragraphs
    try:
        sections = pull_major_sections(
            parsed_text, annotations['sectionheader'])
        paragraphs = literal_eval(annotations['paragraph'])
        paragraphs_df = pd.DataFrame(paragraphs)

        for _, v in enumerate(sections):
            # print(v)
            paragraphs_df.loc[paragraphs_df['start'].between(
                *v[1:]), 'section'] = v[0]
            paragraphs_df['section'] = paragraphs_df['section'].fillna(
                'Unknown')

        paragraphs_df['text'] = parsed_text['paragraph']

        # join paragraphs together
        paragraphs_df = paragraphs_df.groupby('section').agg(
            {
                'text': ' '.join
            }
        )

        parsed_text.update(paragraphs_df.to_dict()['text'])

        return parsed_text

    except:
        return parsed_text


def main(series):

    annotations = series['annotations']

    text = series['text']

    # print('Parsing text')
    parsed_text = parse_text(annotations, text)

    # print('extracting sections')
    parsed_text = connect_paragraphs(parsed_text, annotations)

    return parsed_text


def load_df(file_path):
    df = duckdb.sql(f"SELECT corpusid, content FROM '{file_path}'").fetchdf()
    df = df.set_index('corpusid')
    df.index = df.index.astype('uint64[pyarrow]')
    df = pd.concat([df.drop(['content'], axis=1),
                   df['content'].apply(pd.Series)], axis=1)
    df = df[df['text'].notna()]
    df = df.drop(columns=['source'])
    df['text'] = pd.Series(df['text'], dtype="string[pyarrow]")
    df['annotations'] = df['annotations'].apply(
        lambda x:
            {k: v for k, v in x.items() if k not in ['bibtitle', 'figure', 'bibvenue', 'bibref', 'bibauthorfirstname', 'authoraffiliation', 'authorfirstname',
                                                     'authorlastname', 'bibauthor', 'bibauthorlastname', 'bibentry', 'figurecaption', 'figureref', 'formula', 'publisher', 'table', 'tableref', 'venue']}
    )

    return df


def create_parsed_df(df):
    tqdm.pandas(desc="Dataframe parsing", leave=False)
    cleaned_text = df.progress_apply(main, axis=1)
    cleaned_text = cleaned_text.reset_index()
    cleaned_text.columns = ['corpusid', 'parsed_text']
    cleaned_text = pd.concat([cleaned_text.drop(['parsed_text'], axis=1), cleaned_text['parsed_text'].apply(
        pd.Series)], axis=1).astype('string[pyarrow]')
    write_out_df(cleaned_text, file_path)


def write_out_df(df, file_path):
    parquet_file = re.sub('|'.join(Path(file_path).suffixes),
                          '', str(Path(file_path))) + '.parquet.gzip'
    print(parquet_file)
    df.to_parquet(parquet_file)


if __name__ == "__main__":
    cwd = Path(__file__).parent
    root_dir_name = "therapeutic_accelerator"
    root_dir_path = Path(
        *cwd.parts[: cwd.parts.index("therapeutic_accelerator") + 1])

    fulltext_files = glob(
        str(Path(root_dir_path, 'data/fulltext-zipped/*.json.gz')), recursive=True)

    logging.basicConfig(filename=str(
        Path(root_dir_path, 'logs/parse_full_text.log')), level=logging.INFO)

    for file_path in tqdm(fulltext_files, desc='Processing full text files'):
        try:
            parquet_file = re.sub('|'.join(Path(file_path).suffixes), '', str(
                Path(file_path))) + '.parquet.gzip'
            if not Path(parquet_file).exists():
                df = load_df(file_path)
                create_parsed_df(df)
        except:
            print(f'Could not parse: {file_path}')
            logging.debug(file_path)
