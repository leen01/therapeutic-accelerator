aws cloudformation create-stack --stack-name ta-chroma-stack --template-url https://s3.amazonaws.com/public.trychroma.com/cloudformation/latest/chroma.cf.json
aws cloudformation describe-stacks --stack-name ta-chroma-stack --query 'Stacks[0].Outputs'