---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is. 

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...' (Which dashboards / panels it effects. )
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Desktop (please complete the following information):**
 - OS: [e.g. iOS]
 - Browser [e.g. chrome, safari]
 - Version [e.g. 22]

**Additional context**
Add any other context about the problem here, including BigIP service account permission level, BigIP Versions.

**Attachments**
If the issue is in regards to missing data in dashboards, please also run the following from the installed host and attach the output:

```
curl 'localhost:9090/federate?match[]=%7B__name__%3D~"f5.%2A"%7D'
```

Logs for the collector can be gathered with:
```
docker logs application-study-tool-otel-collector-1 --tail 1000
```
