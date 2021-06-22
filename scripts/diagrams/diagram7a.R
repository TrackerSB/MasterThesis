source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram7.csv", sep = ""))
dat <- anonymize(dat, "author")
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(x = author, y = numsegments)) +
  geom_violin() +
  labs(x = "", y="#Road Segments")
diagram