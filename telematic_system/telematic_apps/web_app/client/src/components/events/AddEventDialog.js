/*
 * Copyright (C) 2019-2022 LEIDOS.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */
import React from 'react';
import { EventFormDialog } from './EventFormDialog';


export const AddEventDialog = (props) => {
    const onCloseHandler = () => {
        props.onCloseEventDialog();
    }

    const onEventSaveHandler = (createdEventInfo) => {
        props.onEventSaveHandler(createdEventInfo);
    }

    return (
        <React.Fragment>
            <EventFormDialog open={props.open} title="Add Event" locationList={props.locationList} testingTypeList={props.testingTypeList}  onEventSaveHandler={onEventSaveHandler} onCloseHandler={onCloseHandler} />
        </React.Fragment >
    )
}
