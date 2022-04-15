from notd.store.retriever import Retriever


class TokenStatisticsProcessor:

    def __init__(self,retriever: Retriever) -> None:
        self.retriever = retriever

    async def calculate_collection_statistics(self, registryAddress: str):
        
        return

