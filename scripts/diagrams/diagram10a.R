source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram10.csv", sep = ""))
dat <- anonymize(dat, "author")
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(x = author, y = numobstacles)) +
  geom_violin() +
  labs(x = "", y = "#Obstacles")
diagram