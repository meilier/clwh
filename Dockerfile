FROM  python:3.7.0
RUN git clone https://github.com/hyperledger/fabric-sdk-py.git && \
    cd fabric-sdk-py && \
    make install
COPY ./requirements.txt /Users/xingweizheng/github/clwh/

RUN cd /Users/xingweizheng/github/clwh/ && \
    pip3 install --no-cache-dir -r requirements.txt

COPY ./ /Users/xingweizheng/github/clwh/
    



