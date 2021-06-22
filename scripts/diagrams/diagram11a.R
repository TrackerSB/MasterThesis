source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram11.csv", sep = ""))
dat <- anonymize(dat, "author")
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(x = author, y = numparticipants)) +
  geom_violin() +
  scale_y_continuous(breaks = seq(1, 4, 1)) +
  labs(x = "", y = "#Participants")
diagram