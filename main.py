from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List

class Pessoa(ABC):
    def __init__(self, nome: str, data_nascimento: str):
        self._nome = nome
        self._data_nascimento = data_nascimento
    
    @property
    def nome(self) -> str:
        return self._nome
    
    @property
    def data_nascimento(self) -> str:
        return self._data_nascimento
    
    @abstractmethod
    def mostrar_dados(self) -> str:
        pass

class Usuario(Pessoa):
    def __init__(self, nome: str, data_nascimento: str, cpf: str, endereco: str):
        super().__init__(nome, data_nascimento)
        self._cpf = self._validar_cpf(cpf)
        self._endereco = endereco
    
    @staticmethod
    def _validar_cpf(cpf: str) -> str:
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        if len(cpf_limpo) != 11:
            raise ValueError("CPF deve conter 11 dígitos")
        return cpf_limpo
    
    @property
    def cpf(self) -> str:
        return self._cpf
    
    @property
    def endereco(self) -> str:
        return self._endereco
    
    def mostrar_dados(self) -> str:
        return f"""\
        Nome: {self.nome}
        Nascimento: {self.data_nascimento}
        CPF: {self.cpf}
        Endereço: {self.endereco}"""

class Conta(ABC):
    _numero_sequencial = 1
    _AGENCIA = "0001"
    
    def __init__(self, usuario: Usuario):
        self._numero = Conta._numero_sequencial
        self._agencia = Conta._AGENCIA
        self._usuario = usuario
        self._saldo = 0.0
        self._extrato: List[str] = []
        self._saques: List[datetime] = []
        Conta._numero_sequencial += 1
    
    @property
    def numero(self) -> int:
        return self._numero
    
    @property
    def agencia(self) -> str:
        return self._agencia
    
    @property
    def usuario(self) -> Usuario:
        return self._usuario
    
    @property
    def saldo(self) -> float:
        return self._saldo
    
    @abstractmethod
    def depositar(self, valor: float) -> None:
        pass
    
    @abstractmethod
    def sacar(self, valor: float) -> None:
        pass
    
    @abstractmethod
    def mostrar_extrato(self) -> str:
        pass

class ContaCorrente(Conta):
    _LIMITE_SAQUES = 3
    _LIMITE_VALOR = 500.0
    
    def __init__(self, usuario: Usuario):
        super().__init__(usuario)
        self._limite_saques = ContaCorrente._LIMITE_SAQUES
        self._limite_valor = ContaCorrente._LIMITE_VALOR
    
    def _validar_saque(self, valor: float) -> bool:
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")
        
        if valor > self.saldo:
            raise ValueError("Saldo insuficiente")
        
        if valor > self._limite_valor:
            raise ValueError(f"Limite por saque: R$ {self._limite_valor:.2f}")
        
        agora = datetime.now()
        saques_24h = [s for s in self._saques if agora - s < timedelta(hours=24)]
        if len(saques_24h) >= self._limite_saques:
            raise ValueError("Limite de saques diários atingido")
        
        return True
    
    def depositar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("Valor do depósito deve ser positivo")
        
        self._saldo += valor
        self._extrato.append(
            f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Depósito: R$ {valor:.2f}"
        )
    
    def sacar(self, valor: float) -> None:
        try:
            self._validar_saque(valor)
            self._saldo -= valor
            self._saques.append(datetime.now())
            self._extrato.append(
                f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Saque: R$ {valor:.2f}"
            )
        except ValueError as e:
            raise e
    
    def mostrar_extrato(self) -> str:
        extrato_str = f"""
        Agência: {self.agencia}
        Conta: {self.numero}
        Titular: {self.usuario.nome}
        CPF: {self.usuario.cpf}
        
        Extrato:
        """
        extrato_str += '\n'.join(self._extrato) if self._extrato else "Nenhuma movimentação"
        extrato_str += f"\n\nSaldo atual: R$ {self.saldo:.2f}"
        return extrato_str

class Banco:
    def __init__(self):
        self._usuarios: List[Usuario] = []
        self._contas: List[ContaCorrente] = []
    
    def cadastrar_usuario(self) -> None:
        try:
            nome = input("Nome completo: ").strip()
            data_nasc = input("Data de nascimento (dd/mm/aaaa): ").strip()
            cpf = input("CPF (apenas números): ").strip()
            endereco = self._montar_endereco()
            
            novo_usuario = Usuario(nome, data_nasc, cpf, endereco)
            
            if any(u.cpf == novo_usuario.cpf for u in self._usuarios):
                print("Erro: CPF já cadastrado")
                return
            
            self._usuarios.append(novo_usuario)
            print("✅ Usuário cadastrado com sucesso!")
        
        except ValueError as e:
            print(f"Erro: {str(e)}")
    
    def _montar_endereco(self) -> str:
        logradouro = input("Logradouro: ").strip()
        nro = input("Número: ").strip()
        bairro = input("Bairro: ").strip()
        cidade = input("Cidade: ").strip()
        uf = input("UF: ").strip().upper()
        return f"{logradouro}, {nro} - {bairro} - {cidade}/{uf}"
    
    def criar_conta(self) -> None:
        cpf = input("CPF do titular: ").strip()
        usuario = next((u for u in self._usuarios if u.cpf == cpf), None)
        
        if not usuario:
            print("Erro: Usuário não encontrado")
            return
        
        nova_conta = ContaCorrente(usuario)
        self._contas.append(nova_conta)
        print(f"✅ Conta {nova_conta.numero} criada com sucesso!")
    
    def listar_contas(self) -> None:
        print("\n═{' CONTAS CADASTRADAS ':=^48}")
        for conta in self._contas:
            print(f"""
            Agência: {conta.agencia}
            Conta: {conta.numero}
            Titular: {conta.usuario.nome}
            Saldo: R$ {conta.saldo:.2f}
            """)
    
    def buscar_conta(self, cpf: str) -> ContaCorrente:
        contas_usuario = [c for c in self._contas if c.usuario.cpf == cpf]
        
        if not contas_usuario:
            raise ValueError("Nenhuma conta encontrada")
        
        print("\nSuas contas:")
        for conta in contas_usuario:
            print(f"Conta {conta.numero} - Saldo: R$ {conta.saldo:.2f}")
        
        while True:
            try:
                numero = int(input("Digite o número da conta: "))
                conta = next(c for c in contas_usuario if c.numero == numero)
                return conta
            except (ValueError, StopIteration):
                print("Conta inválida")

class Interface:
    @staticmethod
    def menu_principal() -> None:
        banco = Banco()
        
        while True:
            print("\n═{' SISTEMA BANCÁRIO ':=^48}")
            print("1 - Novo usuário")
            print("2 - Nova conta")
            print("3 - Operações bancárias")
            print("4 - Listar contas")
            print("5 - Sair")
            
            opcao = input("Opção: ").strip()
            
            if opcao == "1":
                banco.cadastrar_usuario()
            
            elif opcao == "2":
                banco.criar_conta()
            
            elif opcao == "3":
                cpf = input("Digite seu CPF: ").strip()
                try:
                    conta = banco.buscar_conta(cpf)
                    Interface.menu_operacoes(conta)
                except ValueError as e:
                    print(str(e))
            
            elif opcao == "4":
                banco.listar_contas()
            
            elif opcao == "5":
                print("\nObrigado por utilizar nossos serviços!")
                break
            
            else:
                print("Opção inválida")
    
    @staticmethod
    def menu_operacoes(conta: ContaCorrente) -> None:
        while True:
            print("\n═{' OPERAÇÕES ':=^48}")
            print("1 - Depositar")
            print("2 - Sacar")
            print("3 - Extrato")
            print("4 - Voltar")
            
            opcao = input("Opção: ").strip()
            
            try:
                if opcao == "1":
                    valor = float(input("Valor do depósito: "))
                    conta.depositar(valor)
                    print("✅ Depósito realizado")
                
                elif opcao == "2":
                    valor = float(input("Valor do saque: "))
                    conta.sacar(valor)
                    print("✅ Saque realizado")
                
                elif opcao == "3":
                    print(conta.mostrar_extrato())
                
                elif opcao == "4":
                    break
                
                else:
                    print("Opção inválida")
            
            except ValueError as e:
                print(f"Erro: {str(e)}")
            except:
                print("Erro inesperado")

if __name__ == "__main__":
    Interface.menu_principal()