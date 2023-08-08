# Use Python 3.9 as the base image
FROM public.ecr.aws/lambda/python:3.9

WORKDIR /var/task
COPY . .

# Install wget and necessary tools
RUN yum install -y wget curl

# Enable EPEL for Amazon Linux 2
RUN wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum install -y epel-release-latest-7.noarch.rpm

# Install git-lfs
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | bash
RUN yum install -y git-lfs
RUN git lfs install --force

# Clone the Hugging Face model
RUN git clone https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 /var/task/app/models/all-MiniLM-L6-v2
RUN rm -rf /var/task/app/models/all-MiniLM-L6-v2/.git

# Install Python requirements
RUN pip install --no-cache-dir -r requirements.txt

CMD ["app.api.handler"]
