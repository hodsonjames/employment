library(dplyr)
library(data.table)


assignRoleTokens <- function(stringVector,prior,
                             cores=1,thresh=0.1,thresh2=0.1,maxCol = 10,unknown=T,DT=F){
  ## exact same thing as when learning prior! otherwise you might corrupt data
  stringVector[is.na(stringVector)] <- ""
  orginal <- stringVector
  forReturn <- orginal
  proc <- function(stringVector){
    stringVector <- stringr::str_replace_all(stringVector,c("[(]"),replacement = "")
    stringVector <- stringr::str_replace_all(stringVector,c("[)]"),replacement = "")
    stringVector <- stringr::str_replace_all(stringVector,c("&"),replacement = " and ")
    stringVector <- stringr::str_remove(stringVector,",")
    stringVector <- stringr::str_replace_all(stringVector,pattern = "/",replacement = " and ")
    return(stringVector)
  }
  stringVector <- proc(stringVector = stringVector)
  
  # if string is exact match as the one in prior ----------------------------
  firstInd <- stringVector %in% prior$from
  alrdyHave <- stringVector[firstInd]
  ujemanje <- match(alrdyHave,prior$from)
  alrdyHave <- prior[ujemanje,c(1,5:ncol(prior))]
  stringVector <- stringVector[!firstInd]
  alrdyHave$from <- orginal[firstInd]
  orginal <- orginal[!firstInd]
  colnames(alrdyHave) <- c("from",paste0("token",2:ncol(alrdyHave) - 1))
  
  # assiging tokens with matches --------------------------------------------
  ## Necessary step for extracting just things like aa
  if(length(stringVector>0)){ ## so we have new ones
    stringVector <- paste0(" ",stringVector," ")
    #first check if our strings contain anything of our first k most common and assign
    tmpBase <- paste0(" ",prior$from, " ")
    l <- lapply(tmpBase, function(x){
      grepl(x = stringVector,pattern = x,fixed = T)
    }) %>% stringi::stri_list2matrix(.)
    l <- apply(l, 1,function(x){
      a <- which(x=="TRUE")
      if(length(a)==0){
        a <- NA}
      a
    })
    if(class(l) != "list"){
      l1 <- list()
      l1[[1]] <- l
      l <- l1
    }
    ## assign to the most common match
    l <- stringi::stri_list2matrix(l,byrow = T)
    ind <- !apply(l, 1,function(x){all(is.na(x))})
    m <- ncol(prior)
    tmp <- lapply(which(ind), function(x){
      i <- l[x,] %>% na.omit() %>% as.numeric()
      c(orginal[x],as.vector(as.matrix(prior[i,5:m])) %>% na.omit() %>% as.character() %>% unique() %>% sort())
      
    }) 
    rm(l)
    tmp <- stringi::stri_list2matrix(tmp,byrow = T)
    if(ncol(tmp) >maxCol){
      tmp <- tmp[,1:maxCol]
    }
    if(ncol(tmp) > 1){
      colnames(tmp) <- c("from",paste0("token",2:ncol(tmp) - 1))
    }
    tmp <- data.frame(tmp,stringsAsFactors = F)
    stringVector <- stringVector[!ind]
    orginal <- orginal[!ind]
    stringVector <- trimws(stringVector)
  }
  
  
  # check the rest and the ones with just one token ----------------------------------------------------------
  
  if(length(stringVector) > 0){ ## if we have unassigned 
    ## string distance matrix
    distMat <- stringdist::stringdistmatrix(a = stringVector,b=prior$from,method = "jw",p=0.025,nthread = cores)
    help <- apply(distMat, 1,function(x){
      if(min(x) < thresh){ 
        return(prior$org_trans[which.min(x)])
      }else{
        return(NA)
      }
    }
    )
    rm(distMat)
    ii <- data.frame(middle=orginal,help=help,stringsAsFactors = F)
    colnames(ii) <- c("from","org_trans")
    ii <- na.omit(ii)
    ujemanje2 <- match(ii$org_trans,prior$org_trans)
    ii <- cbind(from=ii$from,prior[ujemanje2,5:ncol(prior)],stringsAsFactors=F)
    colnames(ii) <- c("from",paste0("token",2:ncol(ii) - 1))
  }
  
  ##string distance matrix for perhaps more matches of those with just one
  if(exists("tmp")){ ## if there are some worth checking twice
    if(nrow(tmp)>0){
      if(ncol(tmp)>2){
        ind3 <- is.na(tmp[,3])
      }else{
        ind3 <- rep(T,nrow(tmp))
      }
      secondGuess <- tmp[ind3,1]
      if(length(secondGuess>0)){
        second <- proc(secondGuess)
        ## string distance matrix
        distMat <- stringdist::stringdistmatrix(a = second,b=prior$from[!is.na(prior$tokens2)],method = "jw",p=0.025,nthread = cores)
        help <- apply(distMat, 1,function(x){
          if(min(x) < thresh2){ 
            return(prior$org_trans[!is.na(prior$tokens2)][which.min(x)])
          }else{
            return(NA)
          }
        }
        )
        rm(distMat)
        ii2 <- data.frame(middle=secondGuess,help=help,stringsAsFactors = F)
        colnames(ii2) <- c("from","org_trans")
        ind4 <- is.na(ii2$org_trans)
        ii2 <- na.omit(ii2)
        if(nrow(ii2)>0){
          ujemanje3 <- match(ii2$org_trans,prior$org_trans[!is.na(prior$tokens2)])
          ii2 <- cbind(from=ii2$from,prior[!is.na(prior$tokens2),][ujemanje3,5:ncol(prior)],stringsAsFactors = F)
          preglej <- tmp[ind3,1:2]
          preglej <- preglej[!ind4,]
          ii2 <- cbind(preglej,ii2)
          final <- ii2[,1,drop=F]
          preglej <- apply(ii2[,c(-1,-3)], 1,function(x){na.omit(x) %>% unique(.)})
          if(class(preglej)!="list"){
            preglej <- list(preglej=preglej)
          }
          preglej <- stringi::stri_list2matrix(preglej,byrow = T,n_min = ncol(tmp)-1)
          final <- cbind(final,preglej,stringsAsFactors = F)
          colnames(final) <- c("from",paste0("token",2:ncol(final) - 1))
          rows <- which(ind3)
          rows <- rows[which(!ind4)]
          tmp <- as.data.frame(tmp)
          if(ncol(final) > ncol(tmp)){
            hm <- ncol(final) - ncol(tmp)
            for(hm1 in 1:hm){
              tmp <- cbind(tmp,help=rep(NA,nrow(tmp)))
            }
            colnames(tmp) <- c("from",paste0("token",2:ncol(tmp) - 1))
          }
          tmp[rows,] <- final
        }
      }
    }
  }
  
  if(exists("tmp") & exists("ii")){
    tmpDict <- rbindlist(l=list(alrdyHave,tmp,ii),use.names = T,fill=T)
  }else{
    if(exists("tmp") & !exists("ii")){
      tmpDict <- rbindlist(l=list(alrdyHave,tmp),use.names = T,fill=T)
    }
    if(!exists("tmp") & exists("ii")){
      tmpDict <- rbindlist(l=list(alrdyHave,ii),use.names = T,fill=T)
    }
    if(!exists("tmp") & !exists("ii")){
      tmpDict <- data.table(alrdyHave)
    }
  }
  
  
  if(unknown){
    forBind <- forReturn[is.na(match(forReturn,tmpDict$from))]
    if(length(forBind) > 0){
      tmpDict <- rbindlist(l=list(tmpDict,data.frame(from=forBind,stringsAsFactors = F)),use.names = T,fill = T)
      tmpDict <- tmpDict[match(forReturn,tmpDict$from),]
    }
  }
  
  ## strip empty tokens
  tmpDict <- data.frame(tmpDict,stringsAsFactors = F)
  tmpDict <-tmpDict[ ,c(T,T,apply(tmpDict[,3:ncol(tmpDict)], 2,function(x) !all(is.na(x))))]
  
  return(tmpDict)
  
}
#prior <- readRDS("prior.RDS")
#testing
# assignRoleTokens(stringVector = "director of finace",prior=prior)
# assignRoleTokens(stringVector = "directoriiioo",prior=prior)
# assignRoleTokens(stringVector = c("hHAAhh","directora of finaceee"),thresh2 = 0.1,prior=prior)
# assignRoleTokens(stringVector = c("hHAAhh","director of finacee"),thresh2 = 0.1,prior=prior)
# assignRoleTokens(stringVector = c("director","director of finacee"),thresh2 = 0.1,prior=prior)
# assignRoleTokens(stringVector = c("hHAAhh","directora of finace"),thresh2 = 0.1,prior=prior)



