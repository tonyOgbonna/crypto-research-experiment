from agency_swarm import Agency
from ReportAssembler import ReportAssembler
from DataCruncher import DataCruncher
from MarketScanner import MarketScanner
from CryptoSphereCEO import CryptoSphereCEO

ceo = CryptoSphereCEO()
market_scanner = MarketScanner()
data_cruncher = DataCruncher()
report_assembler = ReportAssembler()

agency = Agency([ceo, market_scanner, data_cruncher, report_assembler, [ceo, market_scanner],
                 [ceo, data_cruncher],
                 [market_scanner, data_cruncher],
                 [data_cruncher, report_assembler]],
                shared_instructions='./agency_manifesto.md')

if __name__ == '__main__':
    agency.demo_gradio()