## NPro
v13
Customization for NPro Pte Ltd
### Setup

1. Assignment Rule for Lead and Opportunity

2. Company > NPro Settings > Lead Stale Days for all Active Status

3. Sales Stage > Priority (for Report Display) , Stale days 

4. NPro Settings : For Active Lead Status and Order 

5. Contact > Communication Frequency (in days) for Communication Matrix

6. Auto Email Report for Reports :  Lead Status Reminder and Opportunity Stage Reminder


### Website API for current Open Job Openings

1. Create an api user
2. Pass Authorization header in call to api method /api/method/npro.integrations.job_openings.job_opening
```
    Authorization: api_token:api_secret
```
3. Result will be a list of Job Openings
4. In case of exception, result will have an "exception" property with the exception message. 
5. Add mapping for Business Module in NPro Settings > Business Module Website Service Mapping
#### License

MIT
