from config import ORBITER_CHAINS, ALL_CHAINS_DATA
from termcolor import cprint, colored
import logging


file_log = logging.FileHandler('functions.log', encoding='utf-8')
console_out = logging.StreamHandler()
logging.basicConfig(handlers=(file_log, console_out),
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

def get_network(message:str)-> dict:
    """
    Выбирает сеть для выполнения свапа.
    Принимает:
        message: Сообщение
    Возвращает:
        dict: Название выбранной сети и ее параметры из ORBITER_CHAINS.
    """
    def parse(name:str)-> dict:
        for x in chains_list:
            if x['name']==name:
                return x
        raise "Ошибка, нет такой сети!"

    chains_list = ORBITER_CHAINS['result']
    chains_name = sorted([x['name'] for x in chains_list])
    for key in enumerate(chains_name, 1):
        cprint(f'{key[0]}: {key[1]}','light_green')
    while True:
        try:
            choice = int(input(colored(f"{message} ", 'light_green')))
            if choice < 1 or choice > len(chains_name):
                logging.warning("Некорректное число, повторите ввод!")
            else:
                selected_network = chains_name[choice-1]
                logging.info(f"Вы выбрали сеть {selected_network}")
                return parse(selected_network)
        except ValueError:
            logging.error("Некорректный символ, введите число!")

def get_rpc_explorer(name:str)-> dict:
    for chain in ALL_CHAINS_DATA:
        if chain["name"] == name:
            filtered_data = {}
            # Фильтрация RPC URLs
            filtered_rpc = [url for url in chain.get("rpc", []) if
                            "${INFURA_API_KEY}" not in url and not url.startswith("wss:")]
            filtered_data["rpc"] = filtered_rpc

            # Фильтрация Explorers
            # Фильтрация Explorers URLs
            filtered_explorers = [explorer["url"] for explorer in chain.get("explorers", []) if
                                  not explorer["url"].startswith("wss:")]
            filtered_data["explorers"] = filtered_explorers
            return filtered_data



# def get_token_addr(rpc_url: str, message) -> str:
#     """
#     Получает адрес токена, на который/с которого будет выполнен перевод.
#
#     Параметры:
#         rpc_url (str): URL RPC для подключения к сети.
#
#     Возвращает:
#         str: Адрес токена.
#     """
#     cprint("0 - по умолчанию адрес ETH", 'light_yellow')
#     w3 = Web3(HTTPProvider(rpc_url))
#
#     while True:
#         # Проверка существования токена
#         try:
#             token_address = input(colored(message, 'light_green'))
#             if token_address == '0':
#                 return WETH_ADDRESS
#             # Получение ABI токена (если известен)
#             token_abi = w3.eth.get_code(token_address)
#             if token_abi:
#                 cprint(f"Токен с адресом {token_address} существует.", 'light_green')
#                 return token_address
#             else:
#                 cprint(f"Токен с адресом {token_address} не существует", 'light_yellow')
#                 continue
#         except:
#             cprint(f"Ошибка при проверке токена!", 'light_red')
#
#     async def get_balance(self, token_address:str) -> dict:
#         """
#         Получает баланс кошелька.
#
#         Возвращает:
#             int: Баланс кошелька в wei.
#         """
#
#
#         if token_address in NATIVE_TOKENS_PER_CHAIN:
#             amount_in_wei = await self.w3.eth.get_balance(self.address)
#             decimals = 18
#             self.chain_token = "ETH"
#             return {'amount_in_wei': amount_in_wei, "decimals": decimals, 'name': self.chain_token}
#         else:
#             self.token_contract = self.get_contract(
#                     contract_address=token_address,
#                     abi=GENERAL_ABI)
#             amount_in_wei = await self.token_contract.functions.balanceOf(self.address).call()
#             decimals = await self.token_contract.functions.decimals().call()
#             name = await self.token_contract.functions.name().call()
#             return {'amount_in_wei': amount_in_wei, "decimals": decimals, 'name': name}

def get_amount(balance_decimals_name: dict) -> int:
    """
    Получает количество токена для вывода в wei.

    Параметры:
        balance (int): Баланс в wei.

    Возвращает:
        float: Сумма перевода в нативном токене.
    """
    balance_human = balance_decimals_name['amount_in_wei'] / (10 ** balance_decimals_name['decimals'])
    logging.info(f"На вашем счету: {balance_human:.6f} {balance_decimals_name['name']} токена")
    max_amount = balance_human
    while True:
        try:
            amount = float(input(colored(f"Введите сумму перевода {balance_decimals_name['name']} токена: ", 'light_green')))
            if amount <= 0:
                logging.warning(f"Пожалуйста, введите корректное число.")
                continue
            elif balance_human == 0:
                logging.warning(f"На вашем счету нет токенов")
                exit(1)
            elif max_amount < amount:
                logging.warning(f"Введенная сумма превышает баланс")
                logging.warning(f"Максимальная возможная сумма {max_amount}")
                continue
            return int(amount * (10**balance_decimals_name['decimals']))
        except ValueError:
            logging.error("Пожалуйста, введите корректное число.")

# def get_slippage() -> float:
#     """
#     Получает допустимый процент проскальзывания (Slippage).
#
#     Возвращает:
#         float: Процент проскальзывания.
#     """
#     while True:
#         try:
#             slippage = float(input(colored("Введите допустимый процент проскальзывания (Slippage) в %: ",
#                                            'light_green')))
#             if 0 < slippage < 100:
#                 return slippage
#             else:
#                 cprint("Пожалуйста, введите корректное число.", 'light_yellow')
#         except ValueError:
#             cprint("Пожалуйста, введите корректное число.", 'light_red')

if __name__ == '__main__':
    #print(get_rpc_explorer('OP Sepolia Testnet'))
    print(get_network('Выберите сеть из которой будет сделан трансфер'))
    #get_token_addr('https://arbitrum.llamarpc.com',"Введите адрес токена с которого будем переводить:" )
    #get_amount({'amount_in_wei': 10000000000000000, "decimals": 18, 'name': "ETH"})
    #get_slippage()
    #help(get_slippage)