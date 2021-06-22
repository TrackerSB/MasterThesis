source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram12.csv", sep = ""))
dat <- anonymize(dat, "aiauthor")
dat <- anonymize(dat, "genauthor")
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
diagramColorScheme <- c("SUCCEEDED" = defaultColorSequence[1],
                        "FAILED" = defaultColorSequence[2],
                        "SKIPPED" = defaultColorSequence[3],
                        "TIMEOUT" = defaultColorSequence[4],
                        "NOT MOVING" = defaultColorSequence[5],
                        "ERRORED" = defaultColorSequence[6])
