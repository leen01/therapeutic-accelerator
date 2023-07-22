# Parse text into sections
import json
import re

def get_section_metadata(text, annotations): 
    # Pulls the text from the full text based on the indexes passed in as annotations object.
    sections_list = []
    for i in annotations: 
        section = {}
        section['name'] = text[int(i['start']):int(i['end'])]
        section['start'] = i['start']
        section['end'] = i['end']
        sections_list.append(section)
        
    return sections_list

def find_sections(text_df): 
    # Create annotations index df to parse through
    
    sections_index = json.loads(text_df['annotations_sectionheader'][0])
    
    sections_df = pd.DataFrame(get_section_metadata(text_df['text'][0], sections_index))

    # maintain corpus id as Primary Key in DB
    sections_df['corpusid'] = text_df.corpusid[0]
    
    # rename colum for clarity
    sections_df = sections_df.rename({'name':'section'}, axis = 1)
    
    return sections_df

def refine_sections(section_df): 
    # find relevant sections based on pattern(s)
    pattern = "introduction|methods|results|discussion|conclusion"

    # create a new dataframe to hold values. Will reference original to get last section of text
    section_filter = section_df.section.str.contains(pat = pattern, regex = True, flags=re.IGNORECASE)
    
    # print(section_filter)
    
    if section_filter.isnull().all(): 
        return True

    # only major sections
    sections_df_refined = section_df[section_filter]
    
    # Get indices of sections
    indices = sections_df_refined.index.tolist()

    # Recode values to reflect text location rather than section header
    for i, v in enumerate(indices): 
        # index of section to start text
        start = indices[i]
        
        # Point to stop text, beginning of next section
        # case for last section in entire list
        if i == len(indices)-1:  # for the last section
            end = indices[i] + 1
        else: 
            end = indices[i+1]
        
        sections_df_refined.loc[v, 'start'] = section_df.loc[start, 'end']
        sections_df_refined.loc[v, 'end'] = section_df.loc[end, 'start']
        
    sections_df_refined[['start','end']] = sections_df_refined[['start','end']].astype("int")

    return sections_df_refined

def convert_sections(text, sections_df_refined):
    # Get text for sections
    for i in sections_df_refined.index.tolist():
        start = sections_df_refined.loc[i, 'start']
        end = sections_df_refined.loc[i, 'end']
        
        try: 
            # pull section text to next major section. Remove any new line characters and white space on ends.
            sections_df_refined.loc[i, 'text'] = text[start:end].replace('\n', ' ').strip()
        except: 
            print("could not extract text")
            return ""

    # flatten dataframe into final form
    sections_cleaned = sections_df_refined[['corpusid', 'section', 'text']]
    
    # convert to dataframe with sections as column names
    # sections_cleaned.pivot(index = 'corpusid', columns = 'section', values = 'text').reset_index() 
    
    return sections_cleaned

def extract_sections(row):
    
    if pd.isnull(row.annotations_sectionheader): 
        return np.nan
    
    # convert Pandas to Pandas Dataframe for easier access
    # for tuple iterator
    text_df = pd.DataFrame([dict(row._asdict())])
        
    # get all sections
    sections_df = find_sections(text_df)
    
    # refine only major sections
    try: 
        sections_df_refined = refine_sections(sections_df)
    except: 
        return np.nan
    
    if isinstance(sections_df_refined, bool): 
        # no results found
        return np.nan
    else: 
        try: 
            # convert sections to dataframe with corpusid as the PK and sections column headers
            sections_cleaned = convert_sections(text_df.text[0], sections_df_refined)
        except: 
            return np.nan
    
    return sections_cleaned