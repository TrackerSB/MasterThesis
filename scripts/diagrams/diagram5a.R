source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram5.csv", sep = ""))
print(head(dat))

dat <-
  within(dat, label <-
           ifelse(
             failed == "True",
             "errored",
             ifelse(rejected == "True", "invalid", "valid")
           ))
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(x = author, y = number, fill = label)) +
  geom_bar(stat = "identity") +
  labs(x = "", y = "") +
  scale_fill_manual(values = defaultColorSequence)

diagram