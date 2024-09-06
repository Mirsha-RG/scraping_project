from playwright.sync_api import sync_playwright
import time
import csv
import os

def extract_data():
    try:
        data_page_url = input("Por favor, ingresa la URL de la página de datos: ")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # Navegar a la página de inicio de sesión
            page.goto("https://login.microsoftonline.com/8aaca184-221f-48c0-84cb-3818905e6db0/saml2?SAMLRequest=hVPRbpswFP0V5D4bDDEpWCFV2qxbpHSLFjpVezPmklgydobN0vTrZ5IhdQ%2FN3qyrc%2B49557r2d1rq4Lf0FlpdIHikKAAtDC11LsCPZePOEOBdVzXXBkNBTqBRXfzmeWtOrBF7%2Fb6O%2FzqwbrAN9KWvaaEFKjvNDPcSss0b8EyJ9h28bRmSUjYoTONVL7Inetk1TtgL56ExgZWFmjv3IFF0fF4DI%2BT0HS7KCEkjl6e1luxh5ZjqQdRAkbWoOf6WG4tdM67HCne5oeDCI08yCNuRnRt5e4DOIlIPsAHyM17QYf%2FLsIZYRQKNn9f91JfFn%2BNVl1Aln0pyw3efNuWKHg0nYBzGgVquLJ%2BL0ufidTcnXMddFsvXJmd1GErRWesaZzRSmoIhWmjjHPB44ziJIkbTDNBcEZFhSdZnOUkhWldkWgwlaBgZW0Pq3MCrkAJSSgmGU5ISVIWpyxNf6Lgx3hSyXBSq2WBZI3bxeSt1J%2FNp1U6vYf4bQqbh%2Bq5Pa1TitHlqNi5eTc4arm7vomh4rs2Z6jP00l3QvPRq6yFxUnN85pCw3OoaJbmuUiBwy0nvGpuaZqFsr7wfJhcKBDK9PWwEEbpJGqgnkXvVI13%2F9UPXi03RklxChZKmeNDB9z57%2BG6HlA0v7D%2B%2FSDzPw%3D%3D&RelayState=vVBx&SigAlg=http%3A%2F%2Fwww.w3.org%2F2001%2F04%2Fxmldsig-more%23rsa-sha256&Signature=IwNKsX9jvBl0tvjkhK%2BY%2BbCN1NYxKdoD7gQ3YCGDQUx4XmkBFfSwz97LgKPjaN%2B2XZWRuvFYdXGeY7YTaNApP%2F4z6d09eC13lcj%2BhKSx%2FGx6ootlnuSJ1%2FFdula1HgG9syUqWZmdoariH4Sz5cHe%2Bmo2kQxrOdSU2h3BtSrTv3CSoaB9qqighs9xKgxERJpvxj4zoLkPOkhPWbHCyTbYUJHKPmIwupR1DbnRrMY61MOTOzRgwmp812zM5Jry3u1HiMztF%2FWsE%2BeKXnfZ4k6o1U34gYXzOp3t%2BQdzqVtMD%2BrJ7XkFcpUfRMDZ9Uzx%2FHgeeK1Tkw5JFIeXlPRmrVa2rQ%3D%3D")

            # Realizar el inicio de sesión
            page.fill('input[name="loginfmt"]', "pprimavera@cpamericas.com")
            page.click('input[id="idSIButton9"]')

            # Esperar el campo de contraseña y llenarlo
            page.wait_for_selector('input[name="passwd"]')
            page.fill('input[name="passwd"]', "Usuariodeprueba1*")
            page.click('input[id="idSIButton9"]')

            # Verificar si el botón "No permanecer conectado" existe y es visible
            try:
                if page.query_selector('input[id="idBtn_Back"]'):
                    page.click('input[id="idBtn_Back"]')
                    print("Botón 'No permanecer conectado' fue encontrado y clicado.")
                else:
                    print("El botón 'No permanecer conectado' no está presente.")
            except Exception as e:
                print(f"Error al intentar encontrar o clicar el botón 'No permanecer conectado': {e}")

            # Navegar a la URL de extracción de datos ingresada por el usuario
            page.goto(data_page_url)

            # Esperar hasta que la red esté inactiva
            page.wait_for_load_state('networkidle')

            # Verificar si los elementos están en un iframe
            iframes = page.frames
            found = False

            for frame in iframes:
                record_no_element = frame.query_selector('input[id="oj-collapsible-2-contentrecord_no\\|input"]')
                puc_element = frame.query_selector('input[id="oj-collapsible-2-contentpcr_puc_sdt32\\|input"]')
                property_common_name_element = frame.query_selector('input[id="oj-collapsible-2-contentpcr_propertycode_sdt\\|input"]')
                creation_date_element = frame.query_selector('input[id="oj-collapsible-2-contentuuu_creation_date\\|input"]')
                building_name_element = frame.query_selector('input[id="oj-collapsible-2-contentuBuildingName\\|input"]')
                city_element = frame.query_selector('input[id="oj-collapsible-2-contentugenCityTXT50\\|input"]')
                finding_title_element = frame.query_selector('input[id="oj-collapsible-2-contentfin_findingtitle_tb4000\\|input"]')
                status_element = frame.query_selector('input[id="oj-collapsible-2-contentfin_findingstatus_tb4000\\|input"]')
                current_inspection_element = frame.query_selector('input[id="oj-collapsible-2-contentfin_currentinspection_tb4000\\|input"]')
                tenant_element = frame.query_selector('input[id="oj-collapsible-2-contentugenCompanyNameTB4000\\|input"]')
                erp_customer_number_element = frame.query_selector('input[id="oj-collapsible-2-contentint_erpcustnumber_sdt120\\|input"]')
                organization_type_pd_element = frame.query_selector('input[id="oj-collapsible-2-contentugenCompanyNameTB4000\\|input"]')
                organization_name_element = frame.query_selector('input[id="oj-collapsible-2-contentugenCompanyNameTB4000\\|input"]')
                lease_record_element = frame.query_selector('input[id="oj-collapsible-2-contentugenCompanyNameTB4000\\|input"]')
                lease_title_element = frame.query_selector('input[id="oj-collapsible-2-contentulseNameTB250\\|input"]')
                business_process_record_url_element = frame.query_selector('input[id="oj-collapsible-2-contentuuu_bp_record_url\\|input"]')
                start_date_element = frame.query_selector('input[id="oj-collapsible-3-contentugenStrtdateDOP\\|input"]')
                percentage_complete_to_date_element = frame.query_selector('input[id="oj-collapsible-3-contentuuu_spa_per_comp\\|input"]')
                date_completed_element = frame.query_selector('input[id="oj-collapsible-3-contentulaCompletedDOP\\|input"]')
                item_no_element = frame.query_selector('input[id="oj-collapsible-3-contentlc_itemno_saq\\|input"]')
                finding_type_element = frame.query_selector('input[id="oj-collapsible-3-contentfin_findingtype_tb4000\\|input"]')
                classification_element = frame.query_selector('input[id="oj-collapsible-3-contentfin_classification_tb4000\\|input"]')
                responsible_element = frame.query_selector('input[id="oj-collapsible-3-contentfin_responsible_tb4000\\|input"]')
                responsible_type_element = frame.query_selector('input[id="oj-collapsible-3-contentfin_responsibletype_tb4000\\|input"]')
                required_action_element = frame.query_selector('input[id="oj-collapsible-3-contentulseReqActionTB500\\|input"]')
                location_element = frame.query_selector('input[id="oj-collapsible-3-contentudrLocationTB128\\|input"]')
                comments_element = frame.query_selector('input[id="oj-collapsible-3-contentugenCommentsMTL4000\\|input"]')

                if any([record_no_element, puc_element, property_common_name_element, creation_date_element, building_name_element, city_element, finding_title_element, status_element, current_inspection_element, tenant_element, erp_customer_number_element, organization_type_pd_element, organization_name_element, lease_record_element, lease_title_element, business_process_record_url_element, start_date_element, percentage_complete_to_date_element, date_completed_element, item_no_element, finding_type_element, classification_element, responsible_element, responsible_type_element, required_action_element, location_element, comments_element]):
                    print("Elementos encontrados en un iframe.")
                    found = True
                    break

            if found:
                # Intentar hacer visibles los elementos si están ocultos
                for element in [record_no_element, puc_element, property_common_name_element, creation_date_element, building_name_element, city_element, finding_title_element, status_element, current_inspection_element, tenant_element, erp_customer_number_element, organization_type_pd_element, organization_name_element, lease_record_element, lease_title_element, business_process_record_url_element, start_date_element, percentage_complete_to_date_element, date_completed_element, item_no_element, finding_type_element, classification_element, responsible_element, responsible_type_element, required_action_element, location_element, comments_element]:
                    if element:
                        try:
                            frame.evaluate("el => el.style.display = 'block';", element)
                            time.sleep(2)  # Esperar un poco para asegurar que el cambio de estilo ha ocurrido
                        except Exception as e:
                            print(f"No se pudo modificar el estilo del elemento: {e}")

                record_no = record_no_element.input_value() if record_no_element and record_no_element.is_visible() else "No Visible"
                puc = puc_element.input_value() if puc_element and puc_element.is_visible() else "No Visible"
                property_common_name = property_common_name_element.input_value() if property_common_name_element and property_common_name_element.is_visible() else "No Visible"
                creation_date = creation_date_element.input_value() if creation_date_element and creation_date_element.is_visible() else "No Visible"
                building_name = building_name_element.input_value() if building_name_element and building_name_element.is_visible() else "No Visible"
                city = city_element.input_value() if city_element and city_element.is_visible() else "No Visible"
                finding_title = finding_title_element.input_value() if finding_title_element and finding_title_element.is_visible() else "No Visible"
                status = status_element.input_value() if status_element and status_element.is_visible() else "No Visible"
                current_inspection = current_inspection_element.input_value() if current_inspection_element and current_inspection_element.is_visible() else "No Visible"
                tenant = tenant_element.input_value() if tenant_element and tenant_element.is_visible() else "No Visible"
                erp_customer_number = erp_customer_number_element.input_value() if erp_customer_number_element and erp_customer_number_element.is_visible() else "No Visible"
                organization_type_pd = organization_type_pd_element.input_value() if organization_type_pd_element and organization_type_pd_element.is_visible() else "No Visible"
                organization_name = organization_name_element.input_value() if organization_name_element and organization_name_element.is_visible() else "No Visible"
                lease_record = lease_record_element.input_value() if lease_record_element and lease_record_element.is_visible() else "No Visible"
                lease_title = lease_title_element.input_value() if lease_title_element and lease_title_element.is_visible() else "No Visible"
                business_process_record_url = business_process_record_url_element.input_value() if business_process_record_url_element and business_process_record_url_element.is_visible() else "No Visible"
                start_date = start_date_element.input_value() if start_date_element and start_date_element.is_visible() else "No Visible"
                percentage_complete_to_date = percentage_complete_to_date_element.input_value() if percentage_complete_to_date_element and percentage_complete_to_date_element.is_visible() else "No Visible"
                date_completed = date_completed_element.input_value() if date_completed_element and date_completed_element.is_visible() else "No Visible"
                item_no = item_no_element.input_value() if item_no_element and item_no_element.is_visible() else "No Visible"
                finding_type = finding_type_element.input_value() if finding_type_element and finding_type_element.is_visible() else "No Visible"
                classification = classification_element.input_value() if classification_element and classification_element.is_visible() else "No Visible"
                responsible = responsible_element.input_value() if responsible_element and responsible_element.is_visible() else "No Visible"
                responsible_type = responsible_type_element.input_value() if responsible_type_element and responsible_type_element.is_visible() else "No Visible"
                required_action = required_action_element.input_value() if required_action_element and required_action_element.is_visible() else "No Visible"
                location = location_element.input_value() if location_element and location_element.is_visible() else "No Visible"
                comments = comments_element.input_value() if comments_element and comments_element.is_visible() else "No Visible"

                print(f"Record No.: {record_no}")
                print(f"PUC: {puc}")
                print(f"Property Common Name: {property_common_name}")
                print(f"Creation Date: {creation_date}")
                print(f"Building Name: {building_name}")
                print(f"City: {city}")
                print(f"Finding Title: {finding_title}")
                print(f"Status: {status}")
                print(f"Current Inspection: {current_inspection}")
                print(f"Tenant: {tenant}")
                print(f"ERP Customer Number: {erp_customer_number}")
                print(f"Organization Type PD: {organization_type_pd}")
                print(f"Organization Name: {organization_name}")
                print(f"Lease Record: {lease_record}")
                print(f"Lease Title: {lease_title}")
                print(f"Business Process Record URL: {business_process_record_url}")
                print(f"Start Date: {start_date}")
                print(f"Percentage Complete to Date: {percentage_complete_to_date}")
                print(f"Date Completed: {date_completed}")
                print(f"Item No.: {item_no}")
                print(f"Finding Type: {finding_type}")
                print(f"Classification: {classification}")
                print(f"Responsible: {responsible}")
                print(f"Responsible Type: {responsible_type}")
                print(f"Required Action: {required_action}")
                print(f"Location: {location}")
                print(f"Comments: {comments}")

                # Guardar los datos en un archivo CSV
                with open('extracted_data.csv', 'a', newline='') as file:
                    writer = csv.writer(file)
                    # Escribir el encabezado si el archivo está vacío
                    if file.tell() == 0:
                        writer.writerow([
                            "Record No.", "PUC", "Property Common Name", "Creation Date", "Building Name", "City", 
                            "Finding Title", "Status", "Current Inspection", "Tenant", "ERP Customer Number", 
                            "Organization Type PD", "Organization Name", "Lease Record", "Lease Title", 
                            "Business Process Record URL", "Start Date", "Percentage Complete to Date", 
                            "Date Completed", "Item No.", "Finding Type", "Classification", "Responsible", 
                            "Responsible Type", "Required Action", "Location", "Comments"
                        ])
                    writer.writerow([
                        record_no, puc, property_common_name, creation_date, building_name, city, 
                        finding_title, status, current_inspection, tenant, erp_customer_number, 
                        organization_type_pd, organization_name, lease_record, lease_title, 
                        business_process_record_url, start_date, percentage_complete_to_date, 
                        date_completed, item_no, finding_type, classification, responsible, 
                        responsible_type, required_action, location, comments
                    ])
            else:
                print("Uno o más elementos no fueron encontrados en el DOM.")

            # Cerrar el navegador
            browser.close()

    except Exception as e:
        print(f"Error durante la extracción de datos: {e}")

# Llamada a la función principal
extract_data()




