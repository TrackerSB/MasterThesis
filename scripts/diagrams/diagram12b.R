source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram12.csv", sep = ""))
dat$result <- as.character(dat$result)
dat <-
  within(dat, label <-
           ifelse(
             failed == "True",
             "ERRORED",
             ifelse(
               invalid == "True",
               "INVALID",
               ifelse(result == "UNKNOWN" & status == "TIMEOUT",
                      "TIMEOUT",
                      result)
             )
           ))
print(head(dat))

diagrams = list()
for (r in c(1:8)) {
  print(r)
  diagram <- ggplot(data = subset(dat, round == r),
                    aes(x = genauthor,
                        stat = "identity",
                        fill = label)) +
    geom_bar() +
    labs(x = paste("Round ", r), y = "#Tests") +
    scale_fill_manual(values = defaultColorSequence)
  diagrams[[r]] <- diagram
}
multiplot(plotlist = diagrams, cols = 2)