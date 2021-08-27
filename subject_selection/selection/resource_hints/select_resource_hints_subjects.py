import pandas as pd


df = pd.read_csv("3000_sites_meeting_criteria.csv")

# We take the top 300 subjects in terms of nr of resource hints.
sorted_by_nr_resource_hints_desc = df.sort_values(by="nr_resource_hints", ascending=False)
top300 = sorted_by_nr_resource_hints_desc.iloc[:300]

print(top300[["tranco_url", "browser_url", "source", "nr_resource_hints"]])
top300.to_csv("top300_resource_hints.csv")

# We random take 40 from this list.
random = top300.sample(n=40)
print(random[["tranco_url", "browser_url", "source", "nr_resource_hints"]])



