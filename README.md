# employment
Repository for code related to research projects on global employment dynamics.

## Overview

This repository houses code for the reproduction and exploration of several research projects on global employment dynamics by Anastassia Fedyk, James Hodson, and co-authors at multiple institutions. We chose to maintain one repository since much of the code to pre-process data, many models, and pipelines are shared across projects. This codebase is complementary to the private 'science' library maintained by Cognism Inc., which may be provided to collaborators on these projects. The 'science' library provides a complete enrichment solution from raw resumes and employment profiles to structured json.

## Trading on Talent: Human Capital and Firm Performance

https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3017559

### Abstract

How does a firm's human capital impact financial performance? By directly observing the monthly career migration patterns of 37 million employees of US public companies, along with their education, demographics, and skills, we explore the relationship between performance and two aspects of human capital: turnover and skills. First, we find that firms with higher employee turnover subsequently experience significantly worse returns. Second, firms with a larger emphasis on sales-oriented skills show better subsequent performance, whereas firms with more focus on administrative skills underperform. The effects of skills are heterogeneous across industries, with a larger premium on web development in Information, a higher premium on insurance in Manufacturing, and no benefit from sales-oriented skills in Finance.

### Modules

trading-talent

### Code

This module is split into several parts. Including a replication module to allow the results from the paper to be reproduced over publicly available data; and enrichment modules for improving/modelling several aspects of the data.

#### Replication

Each row of the data represents ~50 features of a firm in a particular month between 2000 and 2018. Features include the skill and demographic makeup of the firm, and changes from the last month. These timeseries are processed by the analysis and regression code to measure the effect of changes in turnover on key company performance indicators through time.

