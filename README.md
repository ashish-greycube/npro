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

<hr>

#### Contact Us  

<a href="https://greycube.in"><img src="https://greycube.in/files/greycube_logo09eade.jpg" width="250" height="auto"></a> <br>
1<sup>st</sup> ERPNext [Certified Partner](https://frappe.io/api/method/frappe.utils.print_format.download_pdf?doctype=Certification&name=PARTCRTF00002&format=Partner%20Certificate&no_letterhead=0&letterhead=Blank&settings=%7B%7D&_lang=en#toolbar=0)
<sub> <img src="https://greycube.in/files/certificate.svg" width="20" height="20"> </sub>
& winner of the [Best Partner Award](https://frappe.io/partners/india/greycube-technologies) <sub> <img src="https://greycube.in/files/award.svg" width="25" height="25"> </sub>

<h5>
<sub><img src="https://greycube.in/files/link.svg" width="20" height="auto"> </sub> <a href="https://greycube.in"> greycube.in</a><br>
<sub><img src="https://greycube.in/files/8665305_envelope_email_icon.svg" width="20" height="18"> </sub> <a href="mailto:sales@greycube.in"> 
 sales@greycube.in</a><br>
<sub><img src="https://greycube.in/files/linkedin1.svg" width="20" height="18"> </sub> <a href="https://www.linkedin.com/company/greycube-technologies"> LinkedIn</a><br>
<sub><img src="https://greycube.in/files/blog.svg" width="20" height="18"> </sub><a href="https://greycube.in/blog"> Blogs</a> </h5>
