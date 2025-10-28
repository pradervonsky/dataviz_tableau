# Tableau syntax & stuff
This markdown helps Tableau users (including me) copy-paste the code from here into their respective calculated fields (or something else).
> Dataset used: [Tableau Sample Superstore]([https://public.tableau.com/app/sample-data/sample_-_superstore.xls)

---
## 1. Calculated Fields
### 1.1. Segment/Categorize
- **Customer Segmentation**
    ```sql
    IF SUM([Sales]) >= 10000 THEN "High Value"
    ELSEIF SUM([Sales]) >= 5000 THEN "Medium Value"
    ELSE "Low Value"
    END
    ```
- **Sign of Profit**
    ```sql
    IF SUM([Profit]) > 0
    THEN "Profitable"
    ELSE "Nonprofitable"
    END
    ```
- **Sales Performance Tier (Quartile)**
    ```sql
    IF SUM([Sales]) > WINDOW_PERCENTILE(SUM([Sales]), 0.75)
    THEN "Top Performer"
    ELSEIF SUM([Sales]) < WINDOW_PERCENTILE(SUM([Sales]), 0.25)
    THEN "Low Performer"
    ELSE "Average Performer"
    END
    ```
- **Delivery Status**
    ```sql
    { FIXED [Order ID] : IF MAX([Ship Date]) <= MAX([Max Order Date])
    THEN "Complete"
    ELSE "Pending"
    END }
    ```
### 1.2. Aggregate data
- **Order Count**
    ```sql
    COUNTD([Order ID])
    ```
- **Customer Count**
    ```sql
    COUNTD([Customer ID])
    ```
- **Cost**
    ```sql
    SUM([Sales]) - SUM([Profit])
    ```
### 1.3. Ratio
- **Profit Ratio**
    ```sql
    SUM([Profit]) / SUM([Sales])
    ```
- **Discount Ratio**
    ```sql
    IF SUM([Sales]) != 0
    THEN SUM([Discount])/SUM([Sales])
    ELSE 0
    END
    ```
### 1.4. Statistical Highlights
- **Sales Winner Highlight**
    ```sql
    IF RANK(SUM([Sales])) = 1
    THEN SUM([Sales])
    END
    ```
- **Sales Min-Max**
    ```sql
    IF SUM([Sales]) = WINDOW_MAX(SUM([Sales]))
    THEN SUM([Sales])
    ELSEIF SUM([Sales]) = WINDOW_MIN(SUM([Sales]))
    THEN SUM([Sales])
    ELSE NULL
    END
    ```
- **Sales Min-Max Labels**
    ```sql
    IF SUM([Sales]) = WINDOW_MAX(SUM([Sales]))
    THEN "Max"
    ELSEIF SUM([Sales]) = WINDOW_MIN(SUM([Sales]))
    THEN "Min"
    ELSE NULL
    END
    ```
---

## 2. Parameter Usage
### 2.1. Swap Measures
- Create a **Parameter** `Measurement List`
    - Data type: `String`
    - Allowable values, select `List`, then in the table below, click to add value:
        - Sales
        - Profit
        - Quantity
- Create a **Set** `Customer in/out` on a field of `[Customer Name]`:
    - Choose **Top** tab
    - Choose **By field** > Top > click `10` (dropdown) > select `Top N`
    - Choose **Category** (dropdown) >  select ` 
- Create a **Calculated Field** `Select Measurement`:
    ```sql
    IF [Measurement List] = "Sales"
    THEN [Sales]
    ELSEIF [Measurement List] = "Profit"
    THEN [Profit]
    ELSEIF [Measurement List] = "Quantity"
    THEN [Quantity]
    END
    ```
- Show Parameter on the [Measurement List] field
### 2.2. Top N
- Create a **Parameter** `Top N`
    - Data type: `Integer`
    - Current value: `10`
    - Allowable values, select `Range`
        - Minimum: `5`
        - Maximum: `15`
        - Step size: `5`
- Create a **Set** `Customer in/out` on a field of `[Customer Name]`:
    - Choose **Top** tab
    - Choose **By field** > Top > click `10` (dropdown) > select `Top N`
    - Click **Category** (dropdown) >  select [Select Measurement]
- Create another **Calculated Field** `Customer Subset Labels`:
    ```sql 
    IF [Customer in/out] = TRUE
    THEN "Top" + STR([Top N]) + "Customer"
    ELSE "Others"
    END
    ```
- Drag [Customer Subset Labels] and then [Customer Name] to Rows shelf
- **Show Parameter** on the [Top N] field
### 2.3. Top N + "Others" grouping
- Create another **Parameter** `Expand/Collapse`
    - Data type: `String`
    - Allowable values, select `List`, then in the table below, click to add value:
        - Expand
        - Collapse
- Create a **Calculated Field** `Customer Top N`:
    ```sql
    IF [Expand/Collapse]="Expand"
    THEN IF [Customer in/out]
    THEN [Customer Name] 
    ELSE "Others" END
    ELSE [Customer Name] END
    ```
- Drag [Customer Top N] to Row shelf to replace [Customer Name]
- **Show Parameter** on the [Expand/Collapse] field