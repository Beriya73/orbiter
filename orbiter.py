import asyncio
import logging
from client import Client
from config import ORBITER_CHAINS, ORBITER_ABI
from functions import get_network, get_rpc_explorer, get_amount
from termcolor import colored
from web3 import AsyncWeb3, AsyncHTTPProvider

# Настройка логирования
file_log = logging.FileHandler('orbiter.log', encoding='utf-8')
console_out = logging.StreamHandler()
logging.basicConfig(handlers=(file_log, console_out),
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

class CustomError(Exception):
    """Base class for other exceptions"""
    pass

class ContractNotFound(CustomError):
    """Raised when the contract is not found"""
    def __init__(self, message="Contract not found!"):
        self.message = message
        super().__init__(self.message)

class InvalidPrivateKey(CustomError):
    """Raised when the private key is invalid"""
    def __init__(self, message="Invalid private key!"):
        self.message = message
        super().__init__(self.message)

class TransactionError(CustomError):
    """Raised when there is an error in the transaction"""
    def __init__(self, message="Transaction error!"):
        self.message = message
        super().__init__(self.message)

class Orbiter(Client):
    def __init__(self, private_key, proxy):
        self.private_key = private_key
        request_kwargs = {'proxy': f'http://{proxy}'}
        self.chain_name_dict = get_network('Select the network from which the native token will be bridged')
        self.chain_name = self.chain_name_dict['name']
        self.chain_token = 'ETH'
        self.chain_id = self.chain_name_dict['chainId']
        self.proxy = proxy
        self.eip_1559 = True
        self.explorer_url = get_rpc_explorer(self.chain_name)['explorers'][0]
        self.rpc_url = get_rpc_explorer(self.chain_name)['rpc'][0]
        try:
            self.w3 = AsyncWeb3(AsyncHTTPProvider(self.rpc_url, request_kwargs=request_kwargs))
            self.address = self.w3.to_checksum_address(self.w3.eth.account.from_key(self.private_key).address)
        except Exception as er:
            logging.error(f"Invalid private key! {er}")
            raise InvalidPrivateKey(f"Invalid private key! {er}")

    async def bridge(self, amount_in_wei_orbiter: int):
        for key in self.chain_name_dict['contracts']:
            if key['name'] == 'OrbiterRouterV3':
                contract_address = key.get('address')
                break
        else:
            raise ContractNotFound

        self.router_contract = self.get_contract(
            contract_address=contract_address, abi=ORBITER_ABI
        )
        try:
            transaction = await self.router_contract.functions.transfers(
                [self.address],
                [amount_in_wei_orbiter],
            ).build_transaction(await self.prepare_tx(amount_in_wei_orbiter))
        except Exception as er:
            logging.error(f"Error creating transaction! {er}")
            raise TransactionError(f"Error creating transaction! {er}")

        # Отправка транзакции
        return await self.send_transaction(transaction)

async def main():
    """
    Основная функция для взаимодействия с пользователем и контрактом Orbiter.
    """
    proxy = ''
    # Получение private_key от пользователя
    private_key = input(colored("Enter your private key: ", 'light_green'))
    orbiter = Orbiter(private_key=private_key, proxy=proxy)
    amount_in_wei = get_amount(await orbiter.get_balance())
    to_chain = get_network("Select the network to which the native token will be bridged:")
    to_chain_id = to_chain.get('internalId')
    if not to_chain_id:
        logging.error("Error getting chainId of the destination network!")
        exit(1)
    amount_in_wei_orbiter = amount_in_wei + 9000 + to_chain_id
    try:
        await orbiter.bridge(amount_in_wei_orbiter)
    except Exception as er:
        logging.error(f"Error transferring native token: {er}")

# Запуск основной функции
asyncio.run(main())
