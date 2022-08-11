

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

