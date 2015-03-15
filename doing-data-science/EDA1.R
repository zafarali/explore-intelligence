# code sketch from Doing Data Science Book

# obtain the data from the server

data1 <- read.csv(url("http://stat.columbia.edu/~rachel/datasets/nyt1.csv"))

# cut converts numerical data into categorial data

data1$ageCat <- cut(data1$Age, c(-Inf, 0, 18, 24, 34, 44, 54, 64, Inf))

library("doBy")

# create our own function to calculate some stats 
siteRange <- function(x){
    c(length(x), min(x), mean(x), max(x))
}

# call summaryBy available in the doBy package
summaryBy(Age~ageCat, data=data1, FUN=siteRange)

clickThroughRate <- function ( impressions, clicks ) {
    clicks/impressions    
}


library("ggplot2")

# data, aes creates aesthetics for mapping
# geom_histogram creates histogram
plot1 <- ggplot(data1, aes(x=Impressions, fill=ageCat))
plot1+geom_histogram(binwidth=1)

data1$hasImpression <- cut(data1$Impressions, c(-Inf, 0, Inf))
summaryBy(Clicks~hasImpression, data=data1, FUN=siteRange)

plot2 <- ggplot(subset(data1, Impressions > 0), aes(x=clickThroughRate(Impressions, Clicks), color=ageCat))
plot2+geom_density()

plot3 <- ggplot(subset(data1, Clicks > 0), aes(x=clickThroughRate(Impressions, Clicks), color=ageCat))
plot3+geom_density()

plot4 <- ggplot(subset(data1, Clicks > 0), aes(x=ageCat, y=Clicks, fill=ageCat))
plot4+geom_boxplot()

plot4 <- ggplot(subset(data1, Clicks > 0), aes(x=Clicks, color=ageCat))
plot4 + geom_density()


