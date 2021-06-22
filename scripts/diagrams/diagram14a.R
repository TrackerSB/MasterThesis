source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram14.csv", sep = ""))
dat <- anonymize(dat, "genauthor")
dat <- anonymize(dat, "aiauthor")
dat <- within(dat, delta <- dateDiff(started, finished, "mins"))
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(x = genauthor, y = delta)) +
  geom_violin() +
  scale_y_continuous(limits = c(0, 7.6)) +
  labs(x = "", y = "Execution time [min]")
diagram