import chromadb


class ChromaConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.chroma = chromadb.ChromaDB(host, port)

    def get_chroma(self):
        return self.chroma

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

if __name__ == "__main__":
    chroma = ChromaConnection("localhost", "5432")
    print(chroma.get_chroma())
    print(chroma.get_host())
    print(chroma.get_port())