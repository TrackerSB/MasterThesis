source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram9.csv", sep = ""))
dat <- anonymize(dat, "author")
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(x = author, y = numroads)) +
  geom_violin() +
  scale_y_continuous(breaks = seq(0, 4, 1)) +
  labs(x = "", y = "#Roads")
diagram