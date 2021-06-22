source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram8.csv", sep = ""))
dat <- anonymize(dat, "author")
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(x = author, y = roadlength)) +
  geom_violin(draw_quantiles = c(.25, .5, .75)) +
  labs(x="", y="Road Length [m]")
diagram