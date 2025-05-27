# Methodologies for Retrieving data from GitHub API

## Limitation Overcoming

### Rate Limit
Checking for the `403` status, along with the header `X-RateLimit-Reset`. If `403` is received, the data retrieval script will sleep until the time specified in `X-RateLimit-Reset`. Moreover, at some point, the script will also check the remaining number of allowed requests from `x-ratelimit-remaining`. If it is less that a hardcoded specified number, sleep until the rate limit is reset. More information can be checked [here](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#checking-the-status-of-your-rate-limit).

## Query Limit
Each query is limited to provide up to [1000 results](https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#about-search) per query even if the pagination is applied. If the pagination is not used, only 30 results will be provided because the default value of `per_page` is 30 and that of `page` is 1.

To get more than 1000 elements, a more fine-grained time range should be applied. For example, instead of querying 1000 repositories per day, 1000 repos per 6 hours should be used.

## Language Task
A main language used in the repository can be retrieved from the key `language`. It is possible that the repo does not detect the language, which will be resulted as `None`. [Ref](https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-repositories)

## The Number of Commits Task
For each repository, a list of commits is retrieved from the `main` branch. There is a limitation of 1000 commits after using a pagination. [Ref](https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits)

## Repo including TDD Task
For each repository, a list of files and folders are retrieved. If there is any file/folder relating to the testing, which the file/folder name of some languages have already been predefined, the repo is assumed to use TDD. [Ref](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#get-repository-content)

## Repo including TDD+CI/CD Task
Including of what is checked from the TDD task, the repository is checked if it contains any file or folder relating to CI/CD task, such as `.github/workflows`.