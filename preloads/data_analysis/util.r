combine_and_reshape_dataframes <- function(monsoon_df, plt_df, no_treatment) {
  REMOVED = "removed"
  INTACT = "intact"
  
  if (nrow(monsoon_df) != nrow(plt_df)) return(FALSE)
  
  # Combine the two dataframes...
  combined <- merge(monsoon_df, plt_df, by.x=c("run", "subject", "device", "browser"), by.y=c("run", "subject", "device", "browser"))
  
  # Add extra row, the treatment for each (subject, run) combo.
  combined$treatment <- (grepl(no_treatment, combined$subject, fixed=TRUE))
  combined$treatment[combined$treatment == TRUE] <- INTACT  
  combined$treatment[combined$treatment == FALSE] <- REMOVED  
  
  # Remove preload & nopreload from subject column
  combined$subject <- sapply(strsplit(combined$subject, '-'), function(x) paste(x[1:2], collapse = '-'))
  
  # Reshape the data
  combined_data <- combined[, c("run", "subject", "treatment", "device", "browser", "energy_joules", "duration_ms", "plt")]
  
  # We sort it accordingly..
  final <- combined_data[order(combined_data$treatment, combined_data$subject, combined_data$run), ]

  # Finally only return the fields we need
  return(final[, c("subject", "treatment", "run", "energy_joules", "plt")])
}

transform_and_test = function(removed, intact, transformation="none", reverse=FALSE) {
  if (reverse==TRUE) {
    removed = max(removed + 1) - removed
    intact = max(intact + 1) - intact
    print("Changed..")
  }
  
  if (transformation == "log") {
    intact_transformed <- log10(intact)
    removed_transformed <- log10(removed)
  } else if (transformation == "sqrt") {
    intact_transformed <- sqrt(intact)
    removed_transformed <- sqrt(removed)
  } else if (transformation == "recip") {
    intact_transformed <- 1 / intact
    removed_transformed <- 1 / removed
  } else {
    intact_transformed <- intact
    removed_transformed <- removed
  }
  
  differences <- removed_transformed - intact_transformed
  hist(differences, main="Transformed")
  qqnorm(differences, main="", xlab = "Normal theoretical quantile", ylab="Energy consumption differences sample quantile (J)")
  qqline(differences)
  print(paste("Transformed: ", transformation))
  print(shapiro.test(differences))
  
  # Skewness 
  print(paste("Skewness after transformation", skewness(differences)))
}
