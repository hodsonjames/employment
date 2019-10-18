library(ggplot2)
library(dplyr)
library(tidyr)
#beta <- readRDS("beta_LDA50.RDS")

multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
  library(grid)
  
  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)
  
  numPlots = length(plots)
  
  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                     ncol = cols, nrow = ceiling(numPlots/cols))
  }
  
  if (numPlots==1) {
    print(plots[[1]])
    
  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))
    
    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
      
      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}


plotWords <- function(beta,k,n=10){
  
  text_top_terms <- beta %>%
    group_by(topic) %>%
    top_n(n, beta) %>%
    ungroup() %>%
    arrange(topic, -beta)
  text_top_terms <- text_top_terms[order(text_top_terms$beta),]
  
  q <- text_top_terms[text_top_terms$topic %in% k,] %>%
    mutate(term = reorder(term, beta)) %>%
    ggplot(aes(term, beta, fill = factor(topic))) +
    geom_col(show.legend = FALSE) +
    facet_wrap(~ topic, scales = "free") +
    coord_flip()
  return(q)
}

#plotWords(beta,c(19,25),15)

plotWordsDiff <- function(beta,k1,k2,n=5){
  
  beta_spread <- beta %>%
    mutate(topic = paste0("topic", topic)) %>%
    spread(topic, beta) %>%
    filter(eval(parse(text=paste0("topic",k1))) > .01 | eval(parse(text=paste0("topic",k2))) > .01) %>%
    mutate(log_ratio = log2(topic2 / topic1))
  
  q <- beta_spread %>%
    group_by(direction = log_ratio > 0) %>%
    top_n(n, abs(log_ratio)) %>%
    ungroup() %>%
    mutate(term = reorder(term, log_ratio)) %>%
    ggplot(aes(term, log_ratio)) +
    geom_col() +
    labs(y = paste0("Log2 ratio of beta in topic", k2, " / topic", k1 )) +
    coord_flip()
  
  return(q)
}

#plotWordsDiff(beta,44,48,10)

wordOnTopic <- function(beta,token){
  if(length(token)==1){
  if(!token %in% beta$term){
    stop("Unknown token!")
  }
  fil <- beta %>% filter(term==token)
  n <- max(fil$beta)
  c <- c(rep(fil$topic,fil$beta*ceiling(10000/n)),fil$topic)
  q <- ggplot(data=data.frame(topic=c),aes(topic)) +  geom_histogram(bins=100) + ylab("Relative weight") + theme(axis.text.y = element_blank())
  return(q)
  }else{
    token <- token[1:2]
    if(!token[1] %in% beta$term){
      stop("Unknown token 1!")
    }
    if(!token[2] %in% beta$term){
      stop("Unknown token 2!")
    }
    fil <- beta %>% filter(term==token[1])
    n <- max(fil$beta)
    c <- c(rep(fil$topic,fil$beta*ceiling(10000/n)),fil$topic)
    q <- ggplot(data=data.frame(topic=c),aes(topic)) +  geom_histogram(bins=100) + ylab("Relative weight") + theme(axis.text.y = element_blank())
    fil2 <- beta %>% filter(term==token[2])
    n2 <- max(fil2$beta)
    c2 <- c(rep(fil2$topic,fil2$beta*ceiling(10000/n2)),fil2$topic)
    q2 <- ggplot(data=data.frame(topic=c2),aes(topic)) +  geom_histogram(bins=100) + ylab("Relative weight") + theme(axis.text.y = element_blank())
    return(multiplot(q,q2,cols=2))
  }
}


phraseOnTopic <- function(phrase,beta,relativeBeta){
  fil <- data.frame(topic=1:50,beta=phrase[1:50])
  n <- max(fil$beta)
  c <- c(rep(fil$topic,fil$beta*ceiling(10000)),fil$topic)
  q <- ggplot(data=data.frame(topic=c),aes(topic)) +  geom_histogram(bins=100) + ylab("Relative weight") +
    theme(axis.text.y = element_blank()) + ggtitle("Normal Beta")
  fil2 <- data.frame(topic=1:50,beta=phrase[51:100])
  n2 <- max(fil2$beta)
  c2 <- c(rep(fil2$topic,fil2$beta*ceiling(10000)),fil2$topic)
  q2 <- ggplot(data=data.frame(topic=c2),aes(topic)) +  geom_histogram(aes(c2),bins=100) + ylab("Relative weight") + 
    theme(axis.text.y = element_blank())  + ggtitle("Relative Beta (Rare Words hold the same weight)")
  
  n <- nrow(fill)
  k1 <- fil$topic[order(fil$beta,decreasing = T)][1:3]
  k2 <- fil2$topic[order(fil2$beta,decreasing = T)][1:3]
  
  a <- plotWords(beta,k1,15)
  b <- plotWords(relativeBeta,k2,15)
  q <- grid.arrange(q, q2,a, b,
               ncol=2, nrow=2, widths=c(6, 6), heights=c(4, 10))
  return(q)
}


assignY <- function(tokens,normal,relative,nTopic=50,ind=1){
  out <- matrix(0,dim(tokens)[1],nTopic)
  out2 <- out
  m <- lapply(1:nrow(tokens), function(i){
    x <- na.omit(tokens[i,])
    tmpA <-normal[normal$term %in% x,]
    tmpB <-relative[relative$term %in% x,]
    alloc <- rep(0,nTopic)
    weights <- rep(0,nTopic)
    for(i in seq(1,nrow(tmpA),nTopic)){
      alloc <- alloc + tmpA$beta[i:(i + nTopic - 1)]
      weights <- weights + tmpB$beta[i:(i + nTopic - 1)]
    }
    return(c(alloc/sum(alloc),weights/sum(weights)))
  }) %>% stringi::stri_list2matrix(.,byrow = T)
  colnames(m) <- paste0("topic",c(1:(2*nTopic)))
  m <- as.data.frame(m)
  m <- apply(m,2,function(x)as.numeric(as.character(x)))
  m <- cbind(m,ind=ind)
  return(as.data.frame(m))
}