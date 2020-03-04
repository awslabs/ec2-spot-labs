#!/bin/bash
sudo -u ec2-user -i <<'EOF'
# Note that "base" is special environment name, include it there as well.
for env in base /home/ec2-user/anaconda3/envs/*; do
    source /home/ec2-user/anaconda3/bin/activate $(basename "$env")
    conda install -y tqdm
    pip install --upgrade boto3 pip
    source /home/ec2-user/anaconda3/bin/deactivate
done

EOF
