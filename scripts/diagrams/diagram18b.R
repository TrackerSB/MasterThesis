source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram18.csv", sep = ""))
dat <- subset(dat, !is.na(finished) & finished != started)
dat$started <- toDatetime(dat$started)
dat$finished <- toDatetime(dat$finished)
dat$minStarted <- -1

for(r in 1:12){
  roundElements <- dat[dat$round == r,]
  minStarted <- min(roundElements$started)
  dat$minStarted <- ifelse(dat$round == r, minStarted, dat$minStarted)
}
dat <- within(dat, relStarted <- started - minStarted)
dat <- within(dat, relFinished <- as.numeric(finished - minStarted))
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(
                    x = relStarted,
                    xend = relFinished,
                    y = round,
                    yend = round
                  )) +
  geom_segment()
diagram