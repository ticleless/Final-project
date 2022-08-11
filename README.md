# devops-02-Final-TeamD-scenario1

# Overview
## Scenario
IoT 디바이스에 설치된 온도, 습도 및 이산화탄소 센서로부터 데이터를 수집하고, 이를 실시간으로 데이터 파이프라인을 이용해 로그 저장소로 전송합니다. 이러한 센서 정보를 시계열 데이터를 기반으로 시각화하여 모니터링해야 합니다.
## Requirements
1.농장주는 실시간 센서 정보를 확인할 수 있어야 합니다. <br>
2.수집/생성 애플리케이션으로부터 발생한 로그가 데이터 파이프라인을 통해 실시간으로 로그 저장소에 전송되어야 합니다.<br>
3.로그는 조건에 맞게 쿼리하여 사용할 수 있어야 합니다. 보통 시계열 기반의 정보를 조회합니다. (예: 지난 7일간 온도 추이)<br>
4.서비스 간의 연결은 서버리스 형태로 구성해야 합니다.
## Resource
### AWS
API Gateway, Lambda, Kinesis Data Stream, Kinesis Firehose, Open Search Service, S3, Open Search dashboard
### IaC
Terraform
## Architecture
![image](https://user-images.githubusercontent.com/55527712/183580369-8380c9fa-651c-4b16-ac1e-3e759c647074.png)

### Step 1: Data Production
***✔ API Gateway to Lambda***

**API Gateway**로 부터 트리거 될 때 **Lambda**가 실행되어서 IoT 디바이스로 부터 수집된 정보들을 **Kinesis Data Stream**으로 레코드를 보내준다. 

### Step 2: Data Pipeline
***✔ Kiensis Data Stream to Kiensis Firehose***

**Data Stream**에 들어온 로그들은 실시간 데이터 스트림을 타고 데이터를 처리 및 전달을 위한 **Firehose**에 도착한다. **Firehose**에 도착한 로그들은 **Open Search Service** 와 백업을 위해 **S3**로 보내지게 된다.



### Step 3: Storing on S3 to lambda

***✔ S3 to Lambda***

**S3**에 로그파일들이 도착할 때 **Lambda**를 트리거하며 로그 파일로 들어온 관찰 값들 중 기준치이상을 초과하게 되면 Discord Webhook alarm을 발생하게 된다.

![Image](https://user-images.githubusercontent.com/55527712/183611090-fd18ea7b-59b3-4716-a7eb-c150f2f465f6.png)

### Step 4: Visualization
***✔ Firehose to Open Search Service & Open Search Dashboard***

**Firehose**로 부터 **Open Search Service**에 도착한 로그들은 Firehose에서 설정한 index로 **Open Search Service**에 자동으로 해당 로그를 가지고 있는 Document가 생성된다. <br>
그렇게 생성된 Document 안에는 매핑된 필드 값들을 통해서 시각화를 시키고자 하는 필드 값으로 **Open Search Dashboard**에서 해당 값을 시각화 시킨다. 
시각화 시킨 필드 값들을 모아서 Custom Dashboard를 구성할 수 있다.
<br>

<img width="696" alt="image" src="https://user-images.githubusercontent.com/55527712/183685606-b888f00a-b046-45bc-914e-e7fafa07814b.png">

## Install Requirements
- AWS 계정이 필요합니다. IAM 사용자일 경우 서비스를 호출하고 관리할 수 있는 권한이 필요합니다.
- AWS CLI 설치 및 configure 구성
- Git 설치
- TerraForm 설치
## Deployment
1. 새 디렉토리를 만들고 해당 디렉토리로 이동한다음 GitHub repository를 Clone합니다.
    ```
    git clone https://github.com/cs-devops-bootcamp/devops-02-Final-TeamD-scenario1.git
    ```
2. 디렉토리를 terraform 디렉토리로 변경합니다.
    ```
    cd terraform
    ```
3. 명령줄에서 terraform init을 입력하여 tf 파일에 구성된 provider에 맞는 플러그인을 다운로드합니다.
    ```
    terraform init
    ```

4. 명령줄에서 terraform을 사용하여 tf 파일에 구성된 대로 AWS 리소스를 배포합니다.
배포 완료까지는 약 15분 소요 될 수 있습니다.
    ```
    terraform apply
    ```
5. Deploy가 완료되면 AWS Management Console에서 Amazon OpenSearch Service로 접속합니다.

6. 배포된 도메인에 해당하는 OpenSearch Dash board URL로 접속합니다.

7. user가 OpenSearch 클러스터와 인덱스에 접근할 수 있도록 하는 권한을 부여하기 위해 먼저 Role을 생성합니다.
![role](https://user-images.githubusercontent.com/78151046/184048274-9f26076b-eedb-4afe-8376-2c7e23b0b6da.jpg)

    - Create Role 
    
    - Name(자유롭게) 작성
    
    - Cluster permissions - `cluster_all`, `indices_all` 부여 
    
    - Index permissions - index에는 `*` 삽입, Index permissions는 Cluster            permissons와 동일하게 권한 부여
    - 나머지 항목은 무시합니다.
8. Role이 생성되면 생성된 Role을 user에 매핑해줘야 함니다.
![mapping](https://user-images.githubusercontent.com/78151046/184048300-30622a82-343b-481c-b2f7-8bcd390bea64.jpg)

    - 생성된 Role name 클릭 ->Mapped users 클릭 -> Manage mapping 클릭
    - Users에 자신이 사용하는 AWS user(사용자) ARN을 삽입합니다. 추가적으로  다른 IAM 사용자도 DashBoard를 구성한다면 그 사용자의 ARN도 삽입합니다.
    - Backend roles는 AWS IAM에서 새로운 역할을 `AmazonOpenSearchFullAccess` 정책을 추가하여 만들고 새로 구성된 Role ARN을 Backend roles에 삽입합니다.

## Index Mapping
OpenSearch Dashboard - Dev tool로 이동하여 아래의 코드를 붙여넣고 실행합니다. `geo_point` data type이 자동으로 매핑되지 않기 때문에 인덱스에 매핑 되기 전 직접 전체 매핑을 해줘야 합니다. `weather`는 변경 가능한 인덱스 명입니다.
```
PUT /weather
{
  "settings": {
    "number_of_shards": 5,
    "number_of_replicas": 1
  },
  
  "mappings": {
      "properties" : {
        "co2" : {
          "type" : "long"
        },
        "coord" : {
          "type": "geo_point"
        },
        "device_id" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "error_code" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "humidity" : {
          "type" : "long"
        },
        "pressure" : {
          "type" : "long"
        },
        "result" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "server_time" : {
          "type" : "date"
        },
        "temperature" : {
          "type" : "long"
        }
      }
    }
}
```
해당 코드를 입력하였다면 OpenSearch Dashboards - Management - Stack Management - Index patterns에 들어갑니다.

Create index pattern을 클릭하고 위의 코드에서 넣었던 인덱스 명을 선택해 인덱스 패턴을 생성합니다.

올바르게 데이터 타입이 들어갔는지 확인합니다.

## How it works
API Gateway 엔드포인트로 GET요청을 보내게 되면 Lambda가 트리거되어 Kinesis Data Stream으로 메세지를 전송합니다. Data Stream을 수신하고 있는 Firehose는 Data Stream의 데이터를 받아 OpenSearch로 전송을 해주고 또한 데이터를 S3에 백업합니다. S3에 데이터가 쌓이면 디스코드 알람을 전송하는 Lambda가 트리거되어 데이터의 값이 기준치를 초과하면 알람을 보내게 됩니다. 데이터가 OpenSearch에 도착하면 OpenSearch Dashboard를 통해 데이터를 시각화하게 됩니다.

## Testing
![test](https://user-images.githubusercontent.com/78151046/184051204-38895242-8d08-4f33-8cdd-56a3d4f5bdc8.jpg)


API gateway로 GET 요청을 보내게되면 해당 스크린샷과 같은 로그가 출력되고 약 1~2분뒤 OpenSearch Dashboard에서 데이터가 시각화되어 나타나는 것을 확인 할 수 있다.

## Clean up
S3 버킷에 데이터가 남아있는 경우 삭제되지 않으므로 버킷 비우기를 한 다음 Clean up을 진행합니다.

terraform 디렉토리에 접근 후 해당 명령어를 입력합니다.
Clean up 또한 약 10여분 걸릴 수 있습니다.
```
terraform destroy
```



## Architecture Resource 
---

> **AWS Lambda**
<br>Lambda는 서버리스 서비스로 서버에 대한 Managed Service를 제공하기 때문에 말 그대로 서버를 신경쓰지 않아도 되기 때문에 서버리스라고 부른다.Lambda를 통해서 아키텍처를 구성함에 있어어 비용과 서버에 대한 관리를 줄이고자 작은 단위의 함수를 실행할 수 있는 Lambda를 선택해서 요청이 들어올때마다 처리해주도록 구현했다. 
  
> **AWS Kiensis Data Stream, Kinesis Firehose**
> <br>Kinesis는 실시간 데이터 스트리밍을 다루는데 유용하고 보다 안정적인 IoT 디바이스에서 오는 정보의 경우 실시간으로 정보가 계속 전달되기 때문에 실시간으로 데이터를 전달 할 수 있는 Kinesis data stream을 사용함으로서 데이터의 안정성을 보장하고 실시간 데이터를 수집 및 저장할 수 있는 리소스를 선택했다.<br>
> Kinesis Firehose는 Kinesis Data Stream으로 부터 데이터를 전달 받아서 처리하고 필요한 destination에 보내주기 위해 Firehose를 사용하였다. Firehose는 데이터를 받아서 별다른 처리 과정 없이 바로 원하는 서비스로 transfer 할 수 있기 때문에 선택했습니다. <br>
> 이 두 리소스를 사용함으로서 실시간으로 메세지를 data stream 에서 firehose로 전달할 수 있고 firehose에서 전달 받은 로그들은 s3에 백업함과 동시에 다른 과정을 거치지 않고 destination인 open search service로 갈 수 있도록 리소스를 구성했습니다.

> **AWS Open Search Service**
> <br> Open Search Service는 실시간으로 유저가 센서의 정보를 보여주고 그 데이터를 시각화 시키기 위한 툴로 Open Serach Service를 사용했습니다. 거의 실시간 대용량 데이터를 시계열 기반으로 원하는 데이터를 시각화 할 수 있고 직관적인 시각화를 제공하기 때문에 이 리소스를 구성했습니다.


## 위의 아키텍처를 통해서
---
IoT Device 센서들로부터 실시간으로 들어오는 데이터를 전달 처리 및 저장하고 해당 내용을 시계열 기반으로 시각화 할 수 있게 리소스들을 구성했습니다. <br>
모든 리소스들을 서버리스 리소스를 사용하여서 서비스간의 커플링을 낮췄습니다.<br>

