# Sistema Bancário POO

Um sistema bancário orientado a objetos em Python que permite gerenciar usuários, contas correntes e operações financeiras básicas, seguindo princípios SOLID e boas práticas de programação.

## 🚀 Funcionalidades

- **Cadastro de Usuários**  
  Armazena: nome, CPF (validado), data de nascimento e endereço completo.
  
- **Criação de Contas**  
  Número sequencial automático, agência fixa "0001", vinculação a usuários existentes.

- **Operações Bancárias**  
  - Depósitos  
  - Saques com limites (R$ 500 por operação, máximo 3 saques/24h)  
  - Extrato detalhado com histórico de transações  

- **Segurança**  
  - Validação de CPF  
  - Encapsulamento de dados sensíveis  
  - Prevenção de duplicidade de CPFs  

## 📋 Requisitos

- Python 3.10+
- Nenhuma dependência externa
