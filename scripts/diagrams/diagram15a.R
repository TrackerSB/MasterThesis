source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram15.csv", sep = ""))
dat <- anonymize(dat, "author")
dat <- within(dat, delta <- dateDiff(started, finished, "mins"))
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(x=author, y=delta))+
  geom_boxplot()+
  labs(x="", y="Execution time [s]")
diagram