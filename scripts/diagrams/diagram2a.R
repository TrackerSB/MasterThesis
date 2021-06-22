source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram2.csv", sep = ""))
print(head(dat))
aiAuthors <- levels(factor(dat$aiauthor))
diagrams <- list()
for(curAuthor in aiAuthors){
  diagram <- ggplot(data = subset(dat, aiauthor == curAuthor), aes(x=generatorauthor, y=travelleddistance)) +
    geom_boxplot() +
    labs(x=curAuthor, y="Travelled distance")
  diagrams[[curAuthor]] <- diagram
}
multiplot(plotlist=diagrams)
