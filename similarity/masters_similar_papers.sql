with token_types as
         (select *
          from ts_token_type('default')),
     token_set as (select *
                   from masters.sample_top_100_abstracts, ts_parse('default', abstract_text) with ordinality),
     lexizing_useful_tokens as
         (select result_id,
                 abstract_text,
                 token,

                 -- to remove stop-words and standardize tokens
                 (ts_lexize('english_stem', token)
                     )[1]   as token_lexized,

                 -- to know the type of token, and keep only words
                 token_types.alias,
                 token_types.description,

                 -- to remember token order
                 ordinality as token_ordinality
          from token_set
                   join token_types using (tokid)
-- removes 7,894 stopwords
          where (ts_lexize('english_stem', token))[1] is not null
            and alias in ('asciiword', 'word', 'asciihword', 'hword')),
     to_compare as (select result_id,
                           abstract_text,
                           string_agg(token_lexized, ' ' order by token_ordinality) as lexized_tokens
                    from lexizing_useful_tokens
                    group by result_id, abstract_text)
select *
from to_compare
-- could also try finding most similar 280 character spans
order by (strict_word_similarity(
                  left(lexized_tokens, 280),
                  (select left(lexized_tokens, 280)
                   from to_compare

                        -- result_id 0 is the paper itself
                   where result_id = 0)
              ) + strict_word_similarity(
                  right(lexized_tokens, 280),
                  (select right(lexized_tokens, 280)
                   from to_compare

                        -- result_id 0 is the paper itself
                   where result_id = 0)
              )) desc
limit 5;