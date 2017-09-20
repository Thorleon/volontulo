import { Component, Inject } from '@angular/core';
import { Router } from '@angular/router';

import { environment } from '../environments/environment';
import { WindowService } from './window.service';


@Component({
  template: ''
})
export class RedirectComponent {
  constructor(
    private router: Router,
    @Inject(WindowService) private window: any
  ) {
    const angularUrlSuffix = this.router.routerState.snapshot.url;
    const djangoUrlSuffix = angularUrlSuffix === '/' ? '' : angularUrlSuffix;
    this.window.location.href = `${environment.djangoRoot}${djangoUrlSuffix}`;
  }
}
