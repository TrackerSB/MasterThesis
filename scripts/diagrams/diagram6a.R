source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram6.csv", sep = ""))
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(x = author,
                      y = number,
                      fill = result)) +
  geom_bar(stat = "identity",
           position = "dodge") +
  labs(x = "", y = "#Tests") +
  guides(fill = guide_legend(title = "Test Result")) +
  scale_fill_manual(values = defaultColorSequence)
diagram