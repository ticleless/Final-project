# Terraform File Directory
```bash
├── terraform
│   ├── ReadMe.md
│   ├── alarm_lambda.tf
│   ├── kinesis.tf
│   ├── provider.tf
│   ├── trigger_lambda.tf
│   └── variables.tf

```
### provider.tf
Terraform 과 AWS 버전을 명시한 테라폼 파일 입니다.
### tirgger_lambda.tf
API Gateway를 통해서 tirgger 됐을 때 해당 센서에 대한 데이터 정보를 data stream에 레코드를 보내는 람다를 구현하는 테라폼 파일 입니다.
### alarm_lambda.tf
실시간 센서 정보가 스토리지에 저장이 됐을 때 데이터 정보들 중 측정하 값이 일정 기준치 이상을 초과할 경우 디스코드로 웹훅 알람을 보내는 람다를 구현하는 테라폼 파일 입니다. 
### kinesis.tf
trigger_lambda로 부터 들어오는 데이터를 저장하고 처리하기 위한 kinesis data stream 과 data stream에서 스트림에 있는 레코드를 소비하고 open search service에 보낼 수 있는 kinesis firehose와 실시간 데이터를 시각화 하고 분석 할 수 있는 Open search service를 구현하는 테라폼 파일 입니다.
### variables.tf
아키텍처를 구현하기에 필요한 환경변수를 지정해놓는 테라폼 파일 입니다.
 
