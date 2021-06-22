source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram13.csv", sep = ""))
dat <- anonymize(dat, "author")
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(x = author, y = goalarea)) +
  geom_boxplot() +
  scale_y_log10() +
  labs(x = "", y = "Size of goal area [m²]")
diagram