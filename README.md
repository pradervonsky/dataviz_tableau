# Tableau syntax & stuff
This markdown helps Tableau users (including me) copy-paste the code from here into their respective calculated fields to create different graphs.

Most of the syntax in here was taken from [help.tableau.com](https://help.tableau.com/current/pro/desktop/en-us/calculations_calculatedfields.htm) using [Superstore Sales]([https://public.tableau.com/app/sample-data/sample_-_superstore.xls) dataset.

---
## 1. Calculated Fields
### 1.1. Segment/Categorize
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
- **Customer Value**
    ```sql
    IF { FIXED [Customer Name] : SUM([Sales]) } >= 10000 THEN "High Value"
    ELSEIF { FIXED [Customer Name] : SUM([Sales]) } >= 5000 THEN "Medium Value"
    ELSE "Low Value"
    END
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
- **Return Ratio**
    ```sql
    COUNTD(IF [Returned] = "Yes"
       THEN [Order ID]
       END)
    / COUNTD([Order ID])
    ```
### 1.4. Statistical Highlights
- **Sales Winner**
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
### 2.1. Year for Delta % Change
- Create a **Parameter** `Year`
    - Data type: `Integer`
    - Current value: `10`
    - Allowable values, select `List`, then in the table below, click to add value:
        `2022, 2023, 2024, 2025`
- Create these calculated fields:
    - **Sales CY**
        ```sql
        IF DATEPART("year", [Order Date]) = [Year]
        THEN [Sales]
        END
        ```
    - **Sales PY**
        ```sql
        IF DATEPART("year", [Order Date]) = ([Year])-1
        THEN [Sales]
        END
        ```
    - **Sales % YoY**
        ```sql
        (SUM([Sales CY]) - SUM([Sales PY]))
        / SUM([Sales PY])
        ```
    - **Sales % YoY Indicators**
        ```sql
        IF [Sales % Chg] > 0
        THEN "▲"
        ELSE "▼"
        END
        ```
### 2.2. Swap Measures
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
### 2.3. Top N
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
### 2.4. Top N + "Others" grouping
- Create another **Parameter** `Expand/Collapse`
    - Data type: `String`
    - Allowable values, select `List`, then in the table below, click to add value:
        - Expand
        - Collapse
- Create a **Calculated Field** `Customer Top N`:
    ```sql
    IF [Expand/Collapse] = "Expand"
    THEN IF [Customer in/out]
         THEN [Customer Name] 
         ELSE "Others"
         END
    ELSE [Customer Name]
    END
    ```
- Drag [Customer Top N] to Row shelf to replace [Customer Name]
- **Show Parameter** on the [Expand/Collapse] field