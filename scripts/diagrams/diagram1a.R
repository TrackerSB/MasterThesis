source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram1.csv", sep = ""))
print(head(dat))

dat <- within(dat, group <- paste(author, allmarkings, sep = "_"))
diagram <- ggplot(data = dat[order(dat$group),],
                  aes(x = author,
                      y = travelleddistance,
                      group = group)) +
  geom_boxplot(ymin = 0,
               ymax = 160,
               position = "dodge2") +
  labs(x = "", y = "Travelled distance")
diagram
