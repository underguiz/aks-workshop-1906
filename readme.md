# Azure Kubernetes Service Workshop

Esse repositório contem instruções e arquivos necessários para executar o workshop de AKS com foco em Scaling, Observabilidade e Operação.

## Labs

Para a execução dos Labs é necessário a istalação do ```kubectl``` e ```az cli```. É possível também a execução utilizando [Azure Cloud Shell](https://azure.microsoft.com/en-us/get-started/azure-portal/cloud-shell/).

Kubectl: 

https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/

https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/

https://kubernetes.io/docs/tasks/tools/install-kubectl-macos/

Az CLI:

https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows

https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux

https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-macos

### Criação de um cluster AKS

Efetue o login na Azure e defina a assinatura onde os recursos serão criados.

```Bash
az login
az account set --subscription "Nome da Assinatura"
```

Crie um resource group para acomodar os recursos .

```Bash
az group create --location "East US" --resource-group "Nome do Resource Group"
```

Crie o cluster de AKS.

```Bash
az aks create --node-count 2 --node-vm-size Standard_B2ms --name "Nome do Cluster" --resource-group "Nome do Resource Group"
```

> O processo de criação irá levar de 5 a 10 minutos.

Quando concluído, obtenha as credenciais do cluster.

```Bash
az aks get-credentials --name "Nome do Cluster" --resource-group "Nome do Resource Group"
```

Confirme que as credenciais foram obtidas e que o cluster está operacional.

```Bash
kubectl get nodes
```

Esse comando deve retornar a lista de nodes.

### Criação de um Deployment e um Service

Crie o deployment de uma aplicação de simulação de stress.

```Bash
kubectl apply -f labs/deployment/web-stress.yaml
```

Observe que foi criado um Pod a partir das instruções do manifesto.

```Bash
kubectl get pods
```

Crie um service para exposição da aplicação.

```Bash
kubectl apply -f labs/deployment/web-stress-service.yaml
```

Observe o serviço criado.

```Bash
kubectl get svc
```

### Autoscaling com aplicação de carga

Cria uma configuração de Horizontal Pod Autoscaler.

```Bash
kubectl apply -f labs/hpa/web-stress-hpa.yaml
```

Observe o objeto criado.

```Bash
kubectl get hpa
```

**Em uma nova aba ou janela do seu terminal**, rode um teste de stress contra o endpoint do simulador de stress.

```Bash
kubectl run -it artillery --image=artilleryio/artillery -- quick -n 3600 -c 50 "http://web-stress-simulator/web-stress-simulator-1.0.0/cpu?time=100"
```

Observe que novos Pods são criados respeitando a configuração do HPA.

```Bash
kubectl get pods -o wide
```

> Alguns pods estarão como pending devido ao fato de não haver recursos suficientes nos nodes. 

Habilite o Cluser Autoscaler no AKS.

```Bash
az aks nodepool update --resource-group "Nome do Resource Group" --cluster-name "Nome do Cluster" --name "nodepool1" --enable-cluster-autoscaler --min-count 1 --max-count 8
```

Após a ativação do Cluster Auto Scaler os pods como pending devem se acomodar nos novos nodes.

```Bash
kubectl get nodes
kubectl get pods
```

Remova o pod do artillery a fim de liberar recursos para o cluster.

```Bash
kubectl delete pod artillery
```

### Grafana + Prometheus

Habilite o Prometheus + Grafana através do portal.

> Azure Kubernetes Service > Monitoring > Enable Prometheus / Enable Container Logs / Enable Grafana

Observe os itens monitorados no Grafana.

> Dashboards > Azure Managed Prometheus

### Azure Monitor + Logs com Kubectl

#### Azure Monitor

Observe os logs utilizando o Log Analytics.

#### Kubectl 

```Bash
kubectl get pods
kubectl logs -f --tail=20 nome-do-pod
```

### Troubeshooting

#### Crash Loop

Crie um Container Registry.

```Bash
az acr create --resource-group "Nome do Resource Group" --name "Nome do Container Registry" --sku Basic
```

Conecte o Container Registry ao seu AKS.

```Bash
az aks update --name "Nome do Cluster" --resource-group "Nome do Resource Group" --attach-acr "Nome do Container Registry"
```

Crie a imagem da aplicação de exemplo.

```Bash
cd labs/troubleshooting/crashloop
az acr build --registry "Nome do Container Registry" --file Dockerfile --image crashloop:v1 .
```

Edite o arquivo ```crashloop.yaml``` para refletir o nome do Container Registry e execute o deployment da aplicação.

```Bash
kubectl apply -f crashloop.yaml
```

Observe que os pods falham ao subir, verifique o erro através dos logs.

```Bash
kubectl get pods -l app=crashloop-app
kubectl logs -l app=crashloop-app
```

Após a correção do problema, crie uma nova imagem da aplicação.

```Bash
az acr build --registry "Nome do Container Registry" --file Dockerfile --image crashloop:v2 .
```

Edite o arquivo ```crashloop.yaml``` para refletir a nova versão (v2) e execute novamente o deployment da aplicação.

```Bash
kubectl apply -f crashloop.yaml
```

Observe que os pods irão subir normalmente.

```Bash
kubectl get pods -l app=crashloop-app
kubectl logs -l app=crashloop-app
```

#### Indisponibilidade

Crie um serviço do tipo load balancer para acessar a aplicação previamente deployada.

```Bash
cd ../load-balancer
kubectl apply -f app-lb.yaml
```

Aguarde o serviço ser criado e acesse o EXTERNAL-IP indicado através do navegador.

```Bash
kubectl get svc
```

A requisição irá sofrer timeout.

#### Debug

É possível acessar os pods em execução para fins de debugs executando o shell de um container.

```Bash
kubectl get pods -l app=crashloop-app
kubectl exec nome-do-pod -it -- /bin/bash
```

Após a correção do problema identificado (targetPort), aplique a correção no manifesto do serviço e aplique novamente.

```Bash
kubectl apply -f app-lb.yaml
```